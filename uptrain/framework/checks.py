"""Implements `Check` objects used for LLM evaluation purposes.
"""
from __future__ import annotations
import os
import typing as t

import polars as pl

from uptrain.operators.base import *
from uptrain.utilities import jsonload, jsondump, to_py_types, clear_directory
from uptrain.framework.base import OperatorDAG, Settings

__all__ = [
    "SimpleCheck",
    "CheckSet",
]


@register_op
class SimpleCheck:
    """A simple check that runs the given list of operators in sequence."""

    name: str
    compute: list[Operator]
    plot: t.Optional[Operator]

    def __init__(
        self,
        name: str,
        compute: list[Operator],
        plot: t.Optional[Operator] = None,
    ):
        """
        Initialize a simple check.

        Args:
            name: Name of the check.
            compute: A list of operators to run in sequence on the input data. The output of each
                operator is passed as input to the next operator.
            plot: How to plot the output of the check.
        """

        self.name = name
        self.compute = compute
        self.plot = plot

    def make_executor(self, settings: Settings) -> "SimpleCheckExecutor":
        """Make an executor for this check."""
        return SimpleCheckExecutor(self, settings)

    def dict(self) -> dict:
        """Serialize this check to a dict."""
        return {
            "name": self.name,
            "compute": [to_py_types(op) for op in self.compute],
            "plot": to_py_types(self.plot),
        }  # serializes only the attributes of the class, like pydantic models

    @classmethod
    def from_dict(cls, data: dict) -> "SimpleCheck":
        """Deserialize a check from a dict of its parameters."""
        compute = [deserialize_operator(op) for op in data["compute"]]

        def get_value(key):
            val = data.get(key, None)
            if val is not None:
                return deserialize_operator(val)
            else:
                return None

        return cls(
            name=data["name"],
            compute=compute,
            plot=get_value("plot"),
        )


class SimpleCheckExecutor:
    """Executor for a check."""

    op: SimpleCheck
    op_dag: OperatorDAG
    settings: "Settings"

    def __init__(self, check: SimpleCheck, settings: "Settings"):
        self.op = check
        self.settings = settings

        # no need to add the plot operator to the dag, since it's run later
        self.op_dag = OperatorDAG(name=check.name)
        for i, op in enumerate(self.op.compute):
            if i == 0:
                deps = []
            else:
                deps = [f"compute_{i-1}"]
            self.op_dag.add_step(f"compute_{i}", op, deps=deps)

    def run(self, data: t.Optional[pl.DataFrame] = None) -> t.Optional[pl.DataFrame]:
        """Run this check on the given data."""

        node_inputs = {"compute_0": data}

        # pick output from the last compute op
        name_final_node = f"compute_{len(self.op.compute) - 1}"
        node_outputs = self.op_dag.run(
            settings=self.settings,
            node_inputs=node_inputs,
            output_nodes=[name_final_node],
        )
        return node_outputs[name_final_node]


class CheckSet:
    source: Operator
    checks: list[SimpleCheck]
    settings: Settings

    def __init__(self, source: Operator, checks: list[t.Any], settings: Settings):
        self.source = source
        self.checks = checks
        self.settings = settings

        # verify all checks have different names
        check_names = [check.name for check in checks]
        assert len(set(check_names)) == len(check_names), "Duplicate check names"

    def get_sink_for_check(self, check: SimpleCheck) -> Operator:
        """Get the sink for the given check."""
        from uptrain.io.writers import JsonWriter

        return JsonWriter(
            fpath=os.path.join(self.settings.logs_folder, f"{check.name}.jsonl")
        )

    def setup(self):
        """Create the logs directory, or clear it if it already exists. Also create sinks for each check."""
        logs_dir = self.settings.logs_folder
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        else:
            clear_directory(logs_dir)
        self.serialize(os.path.join(logs_dir, "config.json"))

    def run(self):
        """Run all checks in this set."""
        source_output = self.source.make_executor(self.settings).run()["output"]
        for check in self.checks:
            check_ouptut = check.make_executor(self.settings).run(source_output)
            sink = self.get_sink_for_check(check)
            sink.make_executor(self.settings).run(check_ouptut)

    @classmethod
    def from_dict(cls, data: dict) -> "CheckSet":
        return cls(
            source=deserialize_operator(data["source"]),
            checks=[deserialize_operator(check) for check in data.get("checks", [])],
            settings=Settings(**data["settings"]),
        )

    def dict(self) -> dict:
        return {
            "source": to_py_types(self.source),
            "checks": [to_py_types(check) for check in self.checks],
            "settings": self.settings.dict(),
        }

    @classmethod
    def deserialize(cls, fpath: str) -> "CheckSet":
        with open(fpath, "r") as f:
            return cls.from_dict(jsonload(f))

    def serialize(self, fpath: t.Optional[str] = None):
        if fpath is None:
            fpath = os.path.join(self.settings.logs_folder, "config.json")

        with open(fpath, "w") as f:
            jsondump(self.dict(), f)
