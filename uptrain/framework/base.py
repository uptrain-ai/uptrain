"""Base constructs used to create user-facing objects.
"""

from __future__ import annotations
import typing as t

from loguru import logger
import networkx as nx
import polars as pl
from pydantic import BaseSettings, Field

from uptrain.operators.base import (
    TYPE_OP_OUTPUT,
    Operator,
    OperatorExecutor,
    deserialize_operator,
)
from uptrain.utilities import to_py_types

__all__ = [
    "OperatorDAG",
    "Settings",
]


class Settings(BaseSettings):
    # uptrain stores logs in this folder
    logs_folder: str = "/tmp/uptrain_logs"

    # external api auth
    openai_api_key: str = Field(None, env="OPENAI_API_KEY")

    # uptrain managed service related
    uptrain_access_token: str = Field(None, env="UPTRAIN_ACCESS_TOKEN")
    uptrain_server_url: str = Field(None, env="UPTRAIN_SERVER_URL")

    def check_and_get(self, key: str) -> str:
        """Check if a value is present in the settings and return it."""
        value = getattr(self, key)
        if value is None:
            raise ValueError(f"Expected value for {key} to be present in the settings.")
        return value


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
