from __future__ import annotations
import os
import sys
import time
import typing as t
import uuid

import evals
import evals.base
import evals.record
import evals.registry
from loguru import logger
from pydantic import BaseModel
import pyarrow as pa

from uptrain.utilities import to_py_types
from .base import check_req_columns_present, TYPE_OP_OUTPUT


# -----------------------------------------------------------
# General purpose OpenAI eval operator
# -----------------------------------------------------------


class UptrainEvalRecorder(evals.record.RecorderBase):
    """Subclass the default OpenAI eval recorder so we don't need to write
    to temporary files.
    """

    list_events: list[dict]
    run_data: dict

    def __init__(self, run_spec: "evals.base.RunSpec"):
        super().__init__(run_spec)
        self.list_events = []
        self.run_data = to_py_types(run_spec)

    def _flush_events_internal(self, events_to_write: t.Sequence["evals.record.Event"]):
        try:
            self.list_events.extend([to_py_types(event) for event in events_to_write])
        except TypeError as e:
            logger.error(f"Failed to serialize events: {events_to_write}")
            raise e
        self._last_flush_time = time.time()
        self._flushes_done += 1

    def record_final_report(self, final_report: t.Any):
        self.run_data["final_report"] = to_py_types(final_report)


class SchemaOpenaiEval(BaseModel):
    col_str_input: str = "input"
    col_str_output: str = "output"
    col_result: str = "output"


class OpenaiEval(BaseModel):
    bundle_path: str
    completion_name: str
    eval_name: str
    schema_data: SchemaOpenaiEval = SchemaOpenaiEval()

    def make_executor(self) -> OpenaiEvalExecutor:
        return OpenaiEvalExecutor(self)


class OpenaiEvalExecutor:
    op: OpenaiEval

    def __init__(self, op: OpenaiEval):
        self.op = op

    def _validate_data(self, data: pa.Table) -> None:
        check_req_columns_present(data, self.op.data_schema)

    def run(self, data: pa.Table) -> TYPE_OP_OUTPUT:
        self._validate_data(data)

        registry = evals.registry.Registry()
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
        recorder.record_final_report(final_report)
        recorder.flush_events()  # NOTE: critical to flush events before exit

        os.remove(path_samples_file)
        return {
            "auxiliary": recorder.run_data,
            "output": pa.Table.from_pylist(recorder.list_events),
        }


# -----------------------------------------------------------
# QnA-specific OpenAI eval operator
# -----------------------------------------------------------


class SchemaQnaEval(BaseModel):
    col_context: str = "context"
    col_question: str = "question"
    col_answer: str = "answer"


class QnaEval(BaseModel):
    prompt_template: str
    schema_data: SchemaQnaEval = SchemaQnaEval()

    def make_executor(self) -> QnaEvalExecutor:
        return QnaEvalExecutor(self)


class QnaEvalExecutor:
    op: QnaEval

    def __init__(self, op: QnaEval):
        self.op = op

    def _validate_data(self, data: pa.Table) -> None:
        check_req_columns_present(data, self.op.data_schema)

    def run(self, data: pa.Table) -> TYPE_OP_OUTPUT:
        self._validate_data(data)
