"""Implements `Check` objects used for LLM evaluation purposes.
"""
from __future__ import annotations
from dataclasses import dataclass
import os
import typing as t

from loguru import logger
import polars as pl
from pydantic import BaseModel

from uptrain.operators.base import *
from uptrain.utilities import jsonload, jsondump, to_py_types, clear_directory
from uptrain.framework.base import OperatorDAG, Settings

__all__ = ["Check", "CheckSet", "ExperimentArgs"]


class Check:
    """A simple check that runs the given list of table operators in sequence.

    Attributes:
        name (str): Name of the check.
        operators (list[TableOp]): A list of operators to run in sequence on the input data. The output of each
            operator is passed as input to the next operator.
        plots (list[Operator]): How to plot the output of the check.
    """

    name: str
    operators: list[Operator]
    plots: list[Operator]

    def __init__(
        self,
        name: str,
        operators: list[Operator],
        plots: t.Union[list[Operator], None] = None,
    ):
        self.name = name
        self.operators = operators
        self.plots = plots if plots is not None else []

    def setup(self, settings: "Settings"):
        self._settings = settings

        # no need to add the plot operator to the dag, since it's run later
        self._op_dag = OperatorDAG(name=self.name)
        for i, op in enumerate(self.operators):
            if i == 0:
                deps = []
            else:
                deps = [f"operator_{i-1}"]
            self._op_dag.add_step(f"operator_{i}", op, deps=deps)
        self._op_dag.setup(settings)

        return self

    def run(self, data: t.Union[pl.DataFrame, None] = None) -> t.Union[pl.DataFrame, None]:
        """Run this check on the given data."""
        node_inputs = {"operator_0": data}

        if len(self.operators):
            # pick output from the last op in the sequence
            name_final_node = f"operator_{len(self.operators) - 1}"
            node_outputs = self._op_dag.run(
                node_inputs=node_inputs,
                output_nodes=[name_final_node],
            )
            return node_outputs[name_final_node]
        else:
            return data

    def dict(self) -> dict:
        """Serialize this check to a dict."""
        return {
            "name": self.name,
            "operators": [to_py_types(op) for op in self.operators],
            "plots": [to_py_types(op) for op in self.plots],
        }  # serializes only the attributes of the class, like pydantic models

    @classmethod
    def from_dict(cls, data: dict) -> "Check":
        """Deserialize a check from a dict of its parameters."""
        operators = [deserialize_operator(op) for op in data["operators"]]
        plots = [deserialize_operator(op) for op in data["plots"]]
        return cls(name=data["name"], operators=operators, plots=plots)  # type: ignore


class CheckSet:
    """Container for a set of checks to run together. This is the entrypoint to Uptrain for users.

    Attributes:
        source (Operator): The source operator to run. Specifies where to get the data from.
        preprocessors (list[TableOp]): A list of operators to run on the input data before running the checks.
        checks (list[Check]): The set of checks to run on the input data.
    """

    source: Operator
    checks: list[Check]
    preprocessors: list[TransformOp]
    postprocessors: list[Operator]

    def __init__(
        self,
        source: Operator,
        checks: list[t.Any],
        preprocessors: t.Union[list[TransformOp], None] = None,
        postprocessors: t.Union[list[Operator], None] = None
    ):
        self.source = source
        self.checks = checks
        self.preprocessors = preprocessors if preprocessors is not None else []
        self.postprocessors = postprocessors if postprocessors is not None else []

        # verify all checks have different names
        check_names = [check.name for check in checks]
        assert len(set(check_names)) == len(check_names), "Duplicate check names"
        for check in checks:
            assert isinstance(check, Check), "Each check must be an instance of Check"

    def setup(self, settings: Settings):
        """Create the logs directory, or clear it if it already exists. Also, persist the
        evaluation config.
        """
        self._settings = settings
        logs_dir = self._settings.logs_folder
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        else:
            clear_directory(logs_dir)

        logger.info(f"Uptrain Logs directory: {logs_dir}")

        # persist the check-set as well as the corresponding settings
        self.serialize(os.path.join(logs_dir, "config.json"))
        self._settings.serialize(os.path.join(logs_dir, "settings.json"))

        self.source.setup(self._settings)
        for preprocessor in self.preprocessors:
            preprocessor.setup(self._settings)
        for check in self.checks:
            check.setup(self._settings)
        for postprocessor in self.postprocessors:
            postprocessor.setup(self._settings)
        return self

    def run(self):
        """Run all checks in this set."""
        from uptrain.operators import JsonWriter

        logger.info("CheckSet Status: Starting checkset")

        source_output = self.source.run()["output"]
        if source_output is None:
            raise RuntimeError("Dataset read from the source is: None")
        if len(source_output) == 0:
            raise RuntimeError("Dataset read from the source is: empty")
        logger.info("CheckSet Status: Dataset loaded from source")

        if len(self.preprocessors) > 0:
            for preprocessor in self.preprocessors:
                source_output = preprocessor.run(source_output)["output"]
                assert source_output is not None, "Output of preprocessor is None"

            # persist the preprocessed input for debugging
            JsonWriter(
                fpath=os.path.join(
                    self._settings.logs_folder, "preprocessed_input.jsonl"
                )
            ).setup(self._settings).run(source_output)

        logger.info("CheckSet Status: Preprocessing Done")

        consolidated_output = {}
        for check in self.checks:
            logger.info(f"CheckSet Status: Check {check.name} Started")
            check_output = check.run(source_output)
            assert check_output is not None, f"Output of check {check.name} is None"
            self._get_sink_for_check(self._settings, check).run(check_output)
            logger.info(f"CheckSet Status: Check {check.name} Completed")

            if len(self.postprocessors):
                if not all(isinstance(op, ColumnOp) for op in check.operators):
                    continue
                for col in check_output.columns:
                    consolidated_output[col] = check_output[col]
        logger.info("CheckSet Status: All Checks Completed")

        if len(self.postprocessors):
            consolidated_output = pl.DataFrame(consolidated_output)
            for postprocessor in self.postprocessors:
                consolidated_output = postprocessor.run(consolidated_output)['output']
                assert consolidated_output is not None, "Output of postprocessor is None"

            # persist the postprocessed input for debugging
            JsonWriter(
                fpath=os.path.join(
                    self._settings.logs_folder, "postprocessed_input.jsonl"
                )
            ).setup(self._settings).run(consolidated_output)
        logger.info("CheckSet Status: Postprocessing Done")

    @staticmethod
    def _get_sink_for_check(settings: Settings, check: Check):
        """Get the sink operator for this check."""
        from uptrain.operators import JsonWriter

        fname = check.name.replace(" ", "_") + ".jsonl"
        return JsonWriter(fpath=os.path.join(settings.logs_folder, fname))

    @classmethod
    def from_dict(cls, data: dict) -> "CheckSet":
        checks = [Check.from_dict(check) for check in data.get("checks", [])]
        return cls(
            source=deserialize_operator(data["source"]),
            preprocessors=[
                deserialize_operator(op) for op in data.get("preprocessors", [])
            ],  # type: ignore
            checks=checks,
            postprocessors=[
                deserialize_operator(op) for op in data.get("postprocessors", [])
            ],  # type: ignore
        )

    def dict(self) -> dict:
        return {
            "source": to_py_types(self.source),
            "preprocessors": [to_py_types(op) for op in self.preprocessors],
            "checks": [check.dict() for check in self.checks],
            "postprocessors": [to_py_types(op) for op in self.postprocessors],
        }

    @classmethod
    def deserialize(cls, fpath: str) -> "CheckSet":
        with open(fpath, "r") as f:
            return cls.from_dict(jsonload(f))

    def serialize(self, fpath: t.Optional[str] = None):
        """Serialize this check set along with the run settings to a JSON file."""
        if fpath is None:
            fpath = os.path.join(self._settings.logs_folder, "config.json")

        with open(fpath, "w") as f:
            jsondump(self.dict(), f)


class ExperimentArgs(BaseModel):
    """Container for arguments to run a LLM experiment. This is the entrypoint to run prompt/model tests with Uptrain for users.
    This generates multiple prompts, generate LLM responses for them and parses the response to add multiple columns.

    Attributes:
        prompt_template (str): Prompt template to generate multiple prompts to experiment with.
        prompt_params (dict(str, str)): Dictionary of prompt variables with experiment with.
        models (str or list[str]): Either a single model or list of models to experiment with.
        context_vars (dict or list): List of dataset variables with mapping between variable name in prompt and variable name in dataset
        temperature (float): Temperature for the LLM response generation.
        col_out_response (str): LLM output will be saved under this column name
        col_out_mapping (dict): Mapping used to parse LLM response
    """

    prompt_template: str
    prompt_params: dict = {}
    models: t.Union[str, list[str]]
    context_vars: t.Union[dict, list]
    temperature: float = 1.0
    col_out_response: str = "response"
    col_out_mapping: t.Optional[dict] = None

    def _get_preprocessors(self):
        from uptrain.operators import PromptGenerator, TextCompletion, OutputParser

        "Convert experiment args into checkset preprocessors for execution"
        if isinstance(self.context_vars, list):
            self.context_vars = dict(zip(self.context_vars, self.context_vars))

        preprocessors = [
            PromptGenerator(
                prompt_template=self.prompt_template,
                prompt_params=self.prompt_params,
                models=[self.models] if isinstance(self.models, str) else self.models,
                context_vars=self.context_vars,
            ),
            TextCompletion(
                col_in_prompt="exp_prompt",
                col_in_model="exp_model",
                col_out_completion=self.col_out_response,
                temperature=self.temperature,
            ),
        ]

        if self.col_out_mapping is not None:
            preprocessors.append(
                OutputParser(
                    col_in_response=self.col_out_response,
                    col_out_mapping=self.col_out_mapping,
                )
            )

        return preprocessors

    def _modify_checks(self, checks):
        "Modify checks to add experiment variables into plots"
        for check in checks:
            if check.plots is not None:
                for plot in check.plots:
                    if plot.kind in ["histogram", "bar", "line"]:
                        if "barmode" not in plot.props:
                            plot.props.update({"barmode": "group"})
                        plot.props["color"] = "exp_experiment_id"
        return checks
