from __future__ import annotations
import os
import typing as t

from loguru import logger
import networkx as nx
import polars as pl
from pydantic import BaseSettings, Field

from uptrain.operators.base import *
from uptrain.utilities import jsonload, jsondump, to_py_types, clear_directory

__all__ = [
    "SimpleCheck",
    "Settings",
    "Config",
]

# -----------------------------------------------------------
# User facing framework objects
# -----------------------------------------------------------


class OperatorDAG:
    """A Graph is a DAG of Uptrain operators, that defines the data pipeline to execute."""

    name: str
    graph: nx.DiGraph
    _node_executors: dict[str, OperatorExecutor]

    def __init__(self, name: str):
        self.name = name
        self.graph = nx.DiGraph()
        # not initialized here, since we need the Settings object to set up the executors
        self._node_executors = {}

    def add_step(
        self, name: str, node: Operator, deps: t.Optional[list[str]] = None
    ) -> None:
        """Add a node to the DAG, along with its dependencies."""
        if name in self.graph.nodes:
            raise ValueError(
                f"Operator with name: {name} already exists in the compute DAG: {self.name}"
            )
        self.graph.add_node(name, op_class=node)

        if deps is None:
            deps = []
        for dep in deps:
            if dep not in self.graph.nodes:
                raise ValueError(
                    f"Specified dependency: {dep} does not exist in the compute DAG: {self.name}"
                )
            self.graph.add_edge(dep, name)

        if not nx.algorithms.dag.is_directed_acyclic_graph(self.graph):
            self.graph.remove_node(name)
            raise ValueError(
                f"Adding a node for operator: {name} creates a cycle in the compute DAG: {self.name}"
            )

    def run(
        self,
        settings: "Settings",
        node_inputs: t.Optional[dict[str, pl.DataFrame]] = None,
        output_nodes: t.Optional[list[str]] = None,
    ) -> dict[str, pl.DataFrame]:
        """Runs the compute DAG.

        Args:
            node_inputs: A dict of input dataframes, keyed by operator name. For other operators, the output
                from the upstream operators is used as input.
            node_outputs: A list of operator names, whose output should be returned.
        """
        if node_inputs is None:
            node_inputs = {}
        if output_nodes is None:
            output_nodes = []

        # dict to hold the output of each node
        node_to_output = {}
        sorted_nodes = list(nx.algorithms.dag.topological_sort(self.graph))
        dependents_count = {
            node_name: len(self._get_node_children(node_name))
            for node_name in sorted_nodes
        }

        # run each node in topological order
        for node_name in sorted_nodes:
            logger.debug(f"Executing node: {node_name} for operator DAG: {self.name}")
            node = self.graph.nodes[node_name]["op_class"]
            # set executors the first time they get used
            if node_name in self._node_executors:
                executor = self._node_executors[node_name]
            else:
                executor = node.make_executor(settings)
                self._node_executors[node_name] = executor

            # get input for this node from its dependencies
            inputs_from_deps = []
            if node_name in node_inputs:
                inputs_from_deps.append(node_inputs[node_name])
            else:
                for dep in self.graph.predecessors(node_name):
                    if dep in node_to_output:
                        inputs_from_deps.append(node_to_output[dep])
                    else:
                        raise ValueError(
                            f"Cannot find output/provided value for dependency: {dep} of node: {node_name}"
                        )

            # run the executor and store the output
            res: "TYPE_OP_OUTPUT" = executor.run(*inputs_from_deps)
            node_to_output[node_name] = res["output"]

            # decrease dependents count for each dependency
            for parent in self.graph.predecessors(node_name):
                dependents_count[parent] -= 1
                if dependents_count[parent] == 0 and parent not in output_nodes:
                    node_to_output.pop(parent, None)

        return {node_name: node_to_output[node_name] for node_name in output_nodes}

    def _get_node_parents(self, name: str) -> list[str]:
        return list(self.graph.predecessors(name))

    def _get_node_children(self, name: str) -> list[str]:
        return list(self.graph.successors(name))

    def __repr__(self) -> str:
        sorted_nodes = list(nx.algorithms.dag.topological_sort(self.graph))
        lines = []
        for node_name in sorted_nodes:
            lines.append(f"{node_name} <- {self._get_node_parents(node_name)}")
        return f"Check: {self.name}\n" + "\n".join(lines)

    def dict(self) -> dict:
        """Serialize this check to a dict."""
        nodes = {
            name: to_py_types(self.graph.nodes[name]["op_class"])
            for name in self.graph.nodes
        }
        edges = list(self.graph.edges)
        return {"name": self.name, "nodes": nodes, "edges": edges}

    @classmethod
    def from_dict(cls, data: dict) -> "OperatorDAG":
        """Deserialize a check from a dict."""
        op_dag = cls(name=data["name"])
        for name, node in data["nodes"].items():
            op_dag.graph.add_node(name, op_class=deserialize_operator(node))
        for edge in data["edges"]:
            assert edge[0] in op_dag.graph.nodes, f"Operator node: {edge[0]} not found"
            assert edge[1] in op_dag.graph.nodes, f"Operator node: {edge[1]} not found"
            op_dag.graph.add_edge(edge[0], edge[1])
        return op_dag


@register_op
class SimpleCheck:
    """A simple check that runs the given list of operators in sequence."""

    name: str
    compute: list[Operator]
    source: t.Optional[Operator]
    sink: t.Optional[Operator]
    plot: t.Optional[Operator]

    def __init__(
        self,
        name: str,
        compute: list[Operator],
        source: t.Optional[Operator] = None,
        sink: t.Optional[Operator] = None,
        plot: t.Optional[Operator] = None,
    ):
        """
        Initialize a simple check.

        Args:
            name: Name of the check.
            compute: A list of operators to run in sequence on the input data. The output of each
                operator is passed as input to the next operator.
            source: Where to read the input data for the check. If absent, data must be passed at runtime manually.
            sink: Where to write the output of the check to.
            plot: How to plot the output of the check.
        """

        self.name = name
        self.compute = compute
        self.source = source
        self.sink = sink
        self.plot = plot

    def make_executor(self, settings: Settings) -> "SimpleCheckExecutor":
        """Make an executor for this check."""
        return SimpleCheckExecutor(self, settings)

    def dict(self) -> dict:
        """Serialize this check to a dict."""
        params = {
            "name": self.name,
            "compute": [to_py_types(op) for op in self.compute],
            "source": to_py_types(self.source),
            "sink": to_py_types(self.sink),
            "plot": to_py_types(self.plot),
        }
        op_name = getattr(self.__class__, "_uptrain_op_name")
        return {"op_name": op_name, "params": params}

    @classmethod
    def from_dict(cls, data: dict) -> "SimpleCheck":
        """Deserialize a check from a dict."""
        data = data["params"]
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
            source=get_value("source"),
            sink=get_value("sink"),
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
        if self.op.source is not None:
            self.op_dag.add_step("source", self.op.source)
        for i, op in enumerate(self.op.compute):
            if i == 0:
                deps = ["source"] if self.op.source is not None else []
            else:
                deps = [f"compute_{i-1}"]
            self.op_dag.add_step(f"compute_{i}", op, deps=deps)
        if self.op.sink is not None:
            self.op_dag.add_step(
                "sink",
                self.op.sink,
                deps=["compute_{}".format(len(self.op.compute) - 1)],
            )

    def run(self, data: t.Optional[pl.DataFrame] = None) -> t.Optional[pl.DataFrame]:
        """Run this check on the given data."""
        # run the source if specified else use the provided data

        if self.op.source is None:
            assert (
                data is not None
            ), f"No source specified for the check: {self.op.name}, so data must be provided manually."
            node_inputs = {"compute_0": data}
        else:
            node_inputs = {}

        # pick output from the last compute op
        name_final_node = f"compute_{len(self.op.compute) - 1}"
        node_outputs = self.op_dag.run(
            settings=self.settings,
            node_inputs=node_inputs,
            output_nodes=[name_final_node],
        )
        return node_outputs[name_final_node]


class Settings(BaseSettings):
    # uptrain stores logs in this folder
    logs_folder: str = "/tmp/uptrain_logs"

    # external api auth
    openai_api_key: str = Field(None, env="OPENAI_API_KEY")

    def check_and_get(self, key: str) -> str:
        """Check if a value is present in the settings and return it."""
        value = getattr(self, key)
        if value is None:
            raise ValueError(f"Expected value for {key} to be present in the settings.")
        return value


class Config:
    checks: list[Operator]
    settings: Settings

    def __init__(self, checks: list[t.Any], settings: Settings):
        # add a default sink to checks without any specified sink
        for check in checks:
            if isinstance(check, SimpleCheck) and check.sink is None:
                import uuid
                from uptrain.io.writers import DeltaWriter

                check.sink = DeltaWriter(
                    fpath=os.path.join(
                        settings.logs_folder, check.name, "-" + str(uuid.uuid4())[:8]
                    )
                )
        self.checks = checks
        self.settings = settings

    def setup(self):
        """Create the logs directory, or clear it if it already exists."""
        logs_dir = self.settings.logs_folder
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        else:
            clear_directory(logs_dir)
        self.serialize(os.path.join(logs_dir, "config.json"))

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        check_objects = []
        for check in data.get("checks", []):
            check_objects.append(deserialize_operator(check))

        settings = Settings(**data["settings"])
        return cls(checks=check_objects, settings=settings)

    def dict(self) -> dict:
        return {
            "checks": [check.dict() for check in self.checks],
            "settings": self.settings.dict(),
        }

    @classmethod
    def deserialize(cls, fpath: str) -> "Config":
        with open(fpath, "r") as f:
            return cls.from_dict(jsonload(f))

    def serialize(self, fpath: t.Optional[str] = None):
        if fpath is None:
            fpath = os.path.join(self.settings.logs_folder, "config.json")

        with open(fpath, "w") as f:
            jsondump(self.dict(), f)
