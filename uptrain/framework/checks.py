"""Implements `Check` objects used for LLM evaluation purposes.
"""
from __future__ import annotations
from dataclasses import dataclass
import os
import typing as t

import polars as pl

from uptrain.operators.base import *
from uptrain.utilities import jsonload, jsondump, to_py_types, clear_directory
from uptrain.framework.base import OperatorDAG, Settings
from uptrain.operators import PlotlyChart

if t.TYPE_CHECKING:
    from uptrain.operators import PromptGenerator

__all__ = [
    "Check",
    "CheckSet",
]


@register_op
class Check(Operator):
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
        plots: list[Operator] | None = None,
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

    def run(self, data: pl.DataFrame | None = None) -> pl.DataFrame | None:
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

    def __init__(
        self,
        source: Operator,
        checks: list[t.Any],
        preprocessors: list[TransformOp] | None = None,
    ):
        self._consolidated_check = Check(
            name="Consolidated Results",
            operators=[],
            plots=[PlotlyChart.Table(title="Consolidated Results")],
        )

        self.source = source
        self.checks = checks
        self.preprocessors = preprocessors if preprocessors is not None else []

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

        # persist the check-set as well as the corresponding settings
        self.serialize(os.path.join(logs_dir, "config.json"))
        self._settings.serialize(os.path.join(logs_dir, "settings.json"))

        self.source.setup(self._settings)
        for preprocessor in self.preprocessors:
            preprocessor.setup(self._settings)
        for check in self.checks:
            check.setup(self._settings)
        self._consolidated_check.setup(self._settings)
        return self

    def run(self):
        """Run all checks in this set."""
        from uptrain.operators.io.writers import JsonWriter

        source_output = self.source.run()["output"]
        assert source_output is not None, "Output of source is None"

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

        consolidated_outputs = source_output
        for check in self.checks:
            check_output = check.run(source_output)
            assert check_output is not None, f"Output of check {check.name} is None"
            self._get_sink_for_check(self._settings, check).run(check_output)

            if all(isinstance(operator, ColumnOp) for operator in check.operators):
                consolidated_outputs = consolidated_outputs.with_columns(
                    [
                        check_output[col_name]
                        for col_name in list(
                            set(check_output.columns)
                            - set(consolidated_outputs.columns)
                        )
                    ]
                )

        self._get_sink_for_check(self._settings, self._consolidated_check).run(
            self._consolidated_check.run(consolidated_outputs)
        )

    @staticmethod
    def _get_sink_for_check(settings: Settings, check: Check):
        """Get the sink operator for this check."""
        from uptrain.operators.io.writers import JsonWriter

        return JsonWriter(
            fpath=os.path.join(settings.logs_folder, f"{check.name}.jsonl")
        )

    @classmethod
    def from_dict(cls, data: dict) -> "CheckSet":
        return cls(
            source=deserialize_operator(data["source"]),
            preprocessors=[
                deserialize_operator(op) for op in data.get("preprocessors", [])
            ],  # type: ignore
            checks=[deserialize_operator(check) for check in data.get("checks", [])],
        )

    def dict(self) -> dict:
        return {
            "source": to_py_types(self.source),
            "preprocessors": [to_py_types(op) for op in self.preprocessors],
            "checks": [to_py_types(check) for check in self.checks],
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
