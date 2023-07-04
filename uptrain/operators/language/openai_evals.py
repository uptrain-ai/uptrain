from __future__ import annotations
import os
import sys
import typing as t
import uuid
import itertools
import numpy as np

import evals
import evals.base
import evals.record
import evals.registry
from loguru import logger
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.utilities import to_py_types

UPTRAIN_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -----------------------------------------------------------
# General purpose OpenAI eval operator. It can take any eval
# specified in the opanai-evals format and run it.
# -----------------------------------------------------------


class UptrainEvalRecorder(evals.record.RecorderBase):
    """Subclass the default OpenAI eval recorder so we don't need to write
    to temporary files.
    """

    _run_data: dict

    def __init__(self, run_spec: "evals.base.RunSpec"):
        super().__init__(run_spec)
        self._run_data = to_py_types(run_spec)

    def get_list_events(self, _type: t.Optional[str] = None) -> list[dict]:
        events = [to_py_types(event) for event in self._events]
        if _type is None:
            return events
        else:
            return [evt for evt in events if evt["type"] == _type]

    def get_run_data(self) -> dict:
        return self._run_data


@register_op
class OpenaiEval(ColumnOp):
    """
    Operator for running OpenAI evals.

    Attributes:
        bundle_path (str): Path to the bundle containing eval resources.
        completion_name (str): Name of the completion function to use.
        eval_name (str): Name of the eval to run.

    """

    bundle_path: str
    completion_name: str
    eval_name: str

    def setup(self, settings: Settings):
        import openai

        openai.api_key = settings.check_and_get("openai_api_key")
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        registry = evals.registry.Registry()
        registry_path = os.path.join(self.bundle_path, "custom_registry")
        registry.add_registry_paths([registry_path])

        eval_name = self.eval_name
        eval_spec = registry.get_eval(eval_name)
        assert (
            eval_spec is not None
        ), f"Eval {eval_name} not found. Available: {list(sorted(registry._evals.keys()))}"

        eval_name = eval_spec.key
        assert eval_name is not None

        # NOTE: create a temporary file with the samples if we are overriding the dataset
        path_samples_file = f"/tmp/{uuid.uuid4()}.jsonl"
        data.write_ndjson(path_samples_file)
        eval_spec.args["samples_jsonl"] = path_samples_file  # type: ignore

        # NOTE: add `custom_fns` to the python path"
        if self.bundle_path not in sys.path:
            sys.path.append(self.bundle_path)
        completion_fns = [self.completion_name]
        completion_fn_instances = [
            registry.make_completion_fn(url) for url in completion_fns
        ]

        run_config = {
            "completion_fns": completion_fns,
            "eval_spec": eval_spec,
            "seed": 42,
            "max_samples": None,
            "command": "",
            "initial_settings": {"visible": True},
        }
        run_spec = evals.base.RunSpec(
            completion_fns=completion_fns,
            eval_name=eval_name,
            base_eval=eval_name.split(".")[0],
            split=eval_name.split(".")[1],
            run_config=run_config,
            created_by="uptrain",
        )
        recorder = UptrainEvalRecorder(run_spec=run_spec)

        eval_class = registry.get_class(eval_spec)
        extra_eval_params = {}
        eval = eval_class(
            completion_fns=completion_fn_instances,
            seed=42,
            name=eval_name,
            registry=registry,
            **extra_eval_params,
        )
        final_report = eval.run(recorder)

        if path_samples_file is not None:
            os.remove(path_samples_file)

        extra = {
            "all_events": recorder.get_list_events(),
            "run_data": recorder.get_run_data(),
            "final_report": to_py_types(final_report),
        }
        unique_types = set(x["type"] for x in recorder.get_list_events())
        for typ in unique_types:
            extra[typ] = pl.from_dicts(
                [
                    x["data"]
                    for x in sorted(
                        recorder.get_list_events(typ),
                        key=lambda x: int(x["sample_id"].split(".")[-1]),
                    )
                ]
            )

        return {"output": None, "extra": extra}


# -----------------------------------------------------------
# Prompt eval operator
# -----------------------------------------------------------


class PromptEval(TransformOp):
    """
    Operator for running prompt-based evaluations.

    Attributes:
        prompt_template (str): Template for the prompt string.
        prompt_variables (list[str]): List of variables to substitute in the prompt template.
        gt_variables (list[str]): List of ground truth variables.
        model_name (str): Name of the model to use for evaluation.
        col_out_prompt (str, optional): Output column name for prompts. Defaults to "prompt".
        col_out_response (str, optional): Output column name for responses. Defaults to "response".
        _settings (Settings): The framework settings.

    """

    prompt_template: str
    prompt_variables: list[str]
    gt_variables: list[str]
    model_name: str
    col_out_prompt: str = "prompt"
    col_out_response: str = "response"
    _settings: Settings

    def setup(self, settings: Settings):
        self._settings = settings
        return self

    def _validate_data(self, data: pl.DataFrame) -> None:
        for col in self.prompt_variables:
            assert (
                col in data.columns
            ), f"Column for the prompt variable: {col} not found in input data."
        for col in self.gt_variables:
            assert (
                col in data.columns
            ), f"Column for the ground truth variable: {col} not found in input data."

    def _construct_prompts(self, data: pl.DataFrame) -> pl.DataFrame:
        prompts = [
            self.prompt_template.format(**{k: row[k] for k in self.prompt_variables})
            for row in data.rows(named=True)
        ]
        return pl.from_dict({"input": prompts})

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        self._validate_data(data)
        prompts = self._construct_prompts(data)

        eval_op = OpenaiEval(
            bundle_path=os.path.join(UPTRAIN_BASE_DIR, "openai_eval_custom"),
            completion_name=self.model_name,
            eval_name="model_run_all",
        )

        eval_op.setup(self._settings)
        oaieval_res = eval_op.run(prompts)
        assert "extra" in oaieval_res and "sampling" in oaieval_res["extra"]
        results = oaieval_res["extra"]["sampling"]

        return {
            "output": data.with_columns(
                [
                    pl.Series(results["prompt"]).alias(self.col_out_prompt),
                    pl.Series(
                        list(itertools.chain(*results["sampled"])),
                    ).alias(self.col_out_response),
                ]
            )
        }
