from __future__ import annotations
import json
import os
import sys
import typing as t
import uuid

import evals
import evals.base
import evals.record
from evals.registry import Registry
from pydantic import BaseModel
import pyarrow as pa


# -----------------------------------------------------------
# General purpose OpenAI eval operator
# -----------------------------------------------------------


class SchemaOpenaiEval(BaseModel):
    col_input: str = "input"
    col_output: str = "output"


class OpenaiEval(BaseModel):
    bundle_path: str
    completion_name: str
    eval_name: str
    data_schema: OpenaiSchema = OpenaiSchema()

    def make_executor(self) -> OpenaiEvalExecutor:
        return OpenaiEvalExecutor(self)


class OpenaiEvalExecutor:
    op: OpenaiEval

    def __init__(self, op: OpenaiEval):
        self.op = op

    def _validate_data(self, data: pa.Table) -> None:
        for col in self.op.data_schema.dict().values():
            assert col in data.column_names, f"Column {col} not found."

    def run(self, data: pa.Table) -> list[dict]:
        """
        FIXME: we want consistent output across all kinds of operators in Uptrain. This should
        return a pyarrow table too.
        """
        registry = Registry()
        registry_path = os.path.join(self.op.bundle_path, "custom_registry")
        registry.add_registry_paths([registry_path])

        eval_name = self.op.eval_name
        eval_spec = registry.get_eval(eval_name)
        assert (
            eval_spec is not None
        ), f"Eval {eval_name} not found. Available: {list(sorted(registry._evals.keys()))}"

        # NOTE: create a temporary file with the samples
        path_samples_file = f"/tmp/{uuid.uuid4()}.jsonl"
        with open(path_samples_file, "w") as samples_file:
            samples_file.write(data.to_pandas().to_json(orient="records", lines=True))
        eval_spec.args["samples_jsonl"] = path_samples_file

        # NOTE: add `custom_fns` to the python path"
        if self.op.bundle_path not in sys.path:
            sys.path.append(self.op.bundle_path)

        completion_fns = [self.op.completion_name]
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

        eval_name = eval_spec.key
        assert eval_name is not None
        run_spec = evals.base.RunSpec(
            completion_fns=completion_fns,
            eval_name=eval_name,
            base_eval=eval_name.split(".")[0],
            split=eval_name.split(".")[1],
            run_config=run_config,
            created_by="uptrain",
        )

        record_path = (
            f"/tmp/{run_spec.run_id}_{self.op.completion_name}_{eval_name}.jsonl"
        )
        recorder = evals.record.LocalRecorder(record_path, run_spec=run_spec)

        eval_class = registry.get_class(eval_spec)
        extra_eval_params = {}
        eval = eval_class(
            completion_fns=completion_fn_instances,
            seed=42,
            name=eval_name,
            registry=registry,
            **extra_eval_params,
        )
        result = eval.run(recorder)
        recorder.record_final_report(result)
        recorder.flush_events()  # NOTE: critical to flush events to the log file
        with open(record_path, "r") as f:
            records = [json.loads(line) for line in f.readlines()]

        os.remove(path_samples_file)
        return records


# -----------------------------------------------------------
# QnA-specific OpenAI eval operator
# -----------------------------------------------------------


class SchemaQnaEval(BaseModel):
    col_context: str = "context"
    col_question: str = "question"
    col_answer: str = "answer"


class QnaEval(BaseModel):
    prompt_template: str
    data_schema: SchemaQnaEval = SchemaQnaEval()

    def make_executor(self) -> QnaEvalExecutor:
        return QnaEvalExecutor(self)


class QnaEvalExecutor:
    op: QnaEval

    def __init__(self, op: QnaEval):
        self.op = op

    def _validate_data(self, data: pa.Table) -> None:
        for attr, col in self.op.data_schema.dict().items():
            assert (
                col in data.column_names
            ), f"Column: {col} for attribute: {attr} not found in input data."

    def run(self, data: pa.Table) -> list[dict]:
        pass
