"""Base constructs used to create user-facing objects.
"""

from __future__ import annotations
import os
import typing as t

from loguru import logger
import networkx as nx
import polars as pl
from pydantic import BaseSettings, Field

from uptrain.operators.base import *
from uptrain.utilities import to_py_types, jsondump, jsonload

__all__ = [
    "OperatorDAG",
    "Settings",
]


class Settings(BaseSettings):
    # uptrain stores logs in this folder
    logs_folder: str = "/tmp/uptrain-logs"

    # external api related
    openai_api_key: str = Field(None, env="OPENAI_API_KEY")
    cohere_api_key: str = Field(None, env="COHERE_API_KEY")
    huggingface_api_key: str = Field(None, env="HUGGINGFACE_API_KEY")
    anthropic_api_key: str = Field(None, env="ANTHROPIC_API_KEY")
    replicate_api_token: str = Field(None, env="REPLICATE_API_TOKEN")

    azure_api_key: str = Field(None, env="AZURE_API_KEY")
    azure_api_base: str = Field(None, env="AZURE_API_BASE")
    azure_api_version: str = Field(None, env="AZURE_API_VERSION")

    openai_rpm_limit: int = 100
    embedding_compute_method: t.Literal['local', 'replicate', 'api'] = 'local'

    # uptrain managed service related
    uptrain_access_token: str = Field(None, env="UPTRAIN_ACCESS_TOKEN")
    uptrain_server_url: str = Field("https://demo.uptrain.ai/", env="UPTRAIN_SERVER_URL")

    # Embedding model related, applicable if embedding_compute_method is api.
    embedding_model_url: str = Field(None, env="EMBEDDING_MODEL_URL")
    embedding_model_api_token: str = Field(None, env="EMBEDDING_MODEL_API_TOKEN")

    # LLM model to run the evaluations
    model: str = "gpt-3.5-turbo"

    # allow additional fields as needed by different operators
    class Config:
        extra = "allow"


    def __init__(self, **data):
        super().__init__(**data)
        if "openai_api_key" in data:
            if data['openai_api_key'] is not None:
                os.environ["OPENAI_API_KEY"] = data["openai_api_key"]
        if "cohere_api_key" in data:
            if data['cohere_api_key'] is not None:
                os.environ["COHERE_API_KEY"] = data["cohere_api_key"]
        if "huggingface_api_key" in data:
            if data['huggingface_api_key'] is not None:
                os.environ["HUGGINGFACE_API_KEY"] = data["huggingface_api_key"]
        if "anthropic_api_key" in data:
            if data['anthropic_api_key'] is not None:
                os.environ["ANTHROPIC_API_KEY"] = data["anthropic_api_key"]
        if "replicate_api_token" in data:
            if data['replicate_api_token'] is not None:
                os.environ["REPLICATE_API_TOKEN"] = data["replicate_api_token"]
        if "embedding_model_api_token" in data:
            if data['embedding_model_api_token'] is not None:
                os.environ["EMBEDDING_MODEL_API_TOKEN"] = data["embedding_model_api_token"]
        if "azure_api_key" in data:
            if data['azure_api_key'] is not None:
                os.environ["AZURE_API_KEY"] = data["azure_api_key"]
        if "azure_api_base" in data:
            if data['azure_api_base'] is not None:
                os.environ["AZURE_API_BASE"] = data["azure_api_base"]
        if "azure_api_version" in data:
            if data['azure_api_version'] is not None:
                os.environ["AZURE_API_VERSION"] = data["azure_api_version"]
        if "uptrain_access_token" in data:
            if data['uptrain_access_token'] is not None:
                os.environ["UPTRAIN_ACCESS_TOKEN"] = data["uptrain_access_token"]
        if "uptrain_server_url" in data:
            if data['uptrain_server_url'] is not None:
                os.environ["UPTRAIN_SERVER_URL"] = data["uptrain_server_url"]

    def check_and_get(self, key: str) -> t.Any:
        """Check if a value is present in the settings and return it."""
        value = getattr(self, key)
        if value is None:
            raise ValueError(f"Expected value for {key} to be present in the settings.")
        return value

    def serialize(self, fpath: str | None = None):
        """Serialize the settings to a json file."""
        if fpath is None:
            fpath = os.path.join(self.logs_folder, "settings.json")
        with open(fpath, "w") as f:
            jsondump(self.dict(), f)

    @classmethod
    def deserialize(cls, fpath: str):
        """Deserialize the settings from a json file."""
        with open(fpath, "r") as f:
            return cls(**jsonload(f))


class OperatorDAG:
    """A Graph is a DAG of Uptrain table operators, that defines the data pipeline to execute."""

    name: str
    graph: nx.DiGraph

    def __init__(self, name: str):
        self.name = name
        self.graph = nx.DiGraph()

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

    def setup(self, settings: "Settings") -> None:
        """Set up the operators in the DAG."""
        sorted_nodes = list(nx.algorithms.dag.topological_sort(self.graph))
        for node_name in sorted_nodes:
            node: "Operator" = self.graph.nodes[node_name]["op_class"]
            node.setup(settings)

    def run(
        self,
        node_inputs: dict[str, pl.DataFrame | None],
        output_nodes: list[str],
    ) -> dict[str, pl.DataFrame]:
        """Runs the compute DAG.
        Args:
            node_inputs: A dict of input dataframes, keyed by operator name. For other operators, the output
                from the upstream operators is used as input.
            node_outputs: A list of operator names, whose output should be returned.
        """

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
            node: "TransformOp" = self.graph.nodes[node_name]["op_class"]

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

            # run the operator and store the output
            res = node.run(*inputs_from_deps)
            node_to_output[node_name] = res["output"]

            # decrease dependents count for each dependency so we don't old onto memory
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
