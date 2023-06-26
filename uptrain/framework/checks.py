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
class SimpleCheck(Operator):
    """A simple check that runs the given list of table operators in sequence."""

    name: str
    sequence: list[TableOp]
    plot: list[Operator]
    _settings: Settings
    _op_dag: OperatorDAG

    def __init__(
        self,
        name: str,
        sequence: list[TableOp],
        plot: list[Operator] | None = None,
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
        self.sequence = sequence
        self.plot = plot if plot is not None else []
        self._settings = None  # type: ignore

        for op in self.sequence:
            if not isinstance(op, TableOp):
                raise ValueError(f"SimpleCheck compute ops must be TableOps, got {op}")

    def setup(self, settings: "Settings"):
        self._settings = settings

        # no need to add the plot operator to the dag, since it's run later
        self._op_dag = OperatorDAG(name=self.name)
        for i, op in enumerate(self.sequence):
            if i == 0:
                deps = []
            else:
                deps = [f"sequence_{i-1}"]
            self._op_dag.add_step(f"sequence_{i}", op, deps=deps)
        self._op_dag.setup(settings)

        return self

    def run(self, data: pl.DataFrame | None = None) -> pl.DataFrame | None:
        """Run this check on the given data."""
        if self._settings is None:
            raise ValueError(f"Must call setup() before running the check: {self.name}")

        node_inputs = {"sequence_0": data}

        # pick output from the last op in the sequence
        name_final_node = f"sequence_{len(self.sequence) - 1}"
        node_outputs = self._op_dag.run(
            node_inputs=node_inputs,
            output_nodes=[name_final_node],
        )
        return node_outputs[name_final_node]

    def dict(self) -> dict:
        """Serialize this check to a dict."""
        return {
            "name": self.name,
            "sequence": [to_py_types(op) for op in self.sequence],
            "plot": [to_py_types(op) for op in self.plot],
        }  # serializes only the attributes of the class, like pydantic models

    @classmethod
    def from_dict(cls, data: dict) -> "SimpleCheck":
        """Deserialize a check from a dict of its parameters."""
        sequence = [deserialize_operator(op) for op in data["sequence"]]
        plot = [deserialize_operator(op) for op in data["plot"]]
        return cls(name=data["name"], sequence=sequence, plot=plot)  # type: ignore


class CheckSet:
    """Container for a set of checks to run together. This is the entrypoint to Uptrain for users.

    Attributes:
        source: The source operator to run. Specifies where to get the data from.
        checks: The list of checks to run on the input data.
        settings: Settings to run this check set with.
    """

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
        for check in checks:
            assert isinstance(
                check, SimpleCheck
            ), "All checks must be an instance of SimpleCheck"

    def _get_sink_for_check(self, check: SimpleCheck) -> Operator:
        """Get the sink for the given check."""
        from uptrain.io.writers import JsonWriter

        return JsonWriter(
            fpath=os.path.join(self.settings.logs_folder, f"{check.name}.jsonl")
        )  # type: ignore

    def setup(self):
        """Create the logs directory, or clear it if it already exists. Also, persist the
        evaluation config.
        """
        logs_dir = self.settings.logs_folder
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        else:
            clear_directory(logs_dir)
        self.serialize(os.path.join(logs_dir, "config.json"))

        for check in self.checks:
            check.setup(self.settings)

        return self

    def run(self):
        """Run all checks in this set."""
        self.source.setup(self.settings)
        source_output = self.source.run()["output"]
        for check in self.checks:
            check_ouptut = check.run(source_output)

            sink = self._get_sink_for_check(check)
            sink.setup(self.settings)
            sink.run(check_ouptut)

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
