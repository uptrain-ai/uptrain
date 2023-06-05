from __future__ import annotations
import os
import typing as t

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


class ComputeOp(t.TypedDict):
    output_cols: list[str]
    operator: Operator


class ComputeOpExec(t.TypedDict):
    output_cols: list[str]
    operator: OperatorExecutor


class Check:
    """An Uptrain Check is a DAG of operators, used to define the data pipeline to execute."""

    name: str
    graph: nx.DiGraph

    def __init__(self, name: str):
        self.name = name
        self.graph = nx.DiGraph()

    def add_step(self, name: str, node: Operator, deps: list[str]) -> None:
        """Add a node to the DAG, along with its dependencies."""
        if name in self.graph.nodes:
            raise ValueError(
                f"An operator with name: {name} has already been added to the Check."
            )

        for dep in deps:
            if dep not in self.graph.nodes:
                raise ValueError(f"Dependency: {dep} does not exist in the Check.")
            self.graph.add_edge(dep, name)
        self.graph.add_node(name, data=node)

        if not nx.algorithms.dag.is_directed_acyclic_graph(self.graph):
            self.graph.remove_node(name)
            raise ValueError("Adding a node for operator: {name} creates a cycle.")

    def run(self) -> None:
        sorted_nodes = list(nx.algorithms.dag.topological_sort(self.graph))
        for node_name in sorted_nodes:
            node_data = self.graph.nodes[node_name]["data"]
            node_data.run()

    def _get_node_parents(self, name: str) -> list[str]:
        return list(self.graph.predecessors(name))

    def _get_node_descendants(self, name: str) -> list[str]:
        return list(nx.algorithms.dag.descendants(self.graph, name))

    def __repr__(self) -> str:
        sorted_nodes = list(nx.algorithms.dag.topological_sort(self.graph))
        lines = []
        for node_name in sorted_nodes:
            lines.append(f"{node_name} <- {self._get_node_parents(node_name)}")
        return f"Check: {self.name}" + "\n".join(lines)

    def dict(self) -> dict:
        """Serialize this check to a dict."""
        nodes = {
            name: to_py_types(self.graph.nodes[name]["data"])
            for name in self.graph.nodes
        }
        edges = list(self.graph.edges)
        return {"name": self.name, "nodes": nodes, "edges": edges}

    @classmethod
    def from_dict(cls, data: dict) -> "Check":
        """Deserialize a check from a dict."""
        check = cls(name=data["name"])
        for name, node in data["nodes"].items():
            check.graph.add_node(name, data=deserialize_operator(node))
        for edge in data["edges"]:
            assert edge[0] in check.graph.nodes, f"Operator node: {edge[0]} not found"
            assert edge[1] in check.graph.nodes, f"Operator node: {edge[1]} not found"
            check.graph.add_edge(edge[0], edge[1])
        return check


@register_op
class SimpleCheck:
    """A simple check that runs the given list of operators in sequence. Can be used directly
    when you don't need much customization.
    """

    # name of the check
    name: str
    # specify the sequence of operators to run, and name(s) for the output columns from each
    compute: list[ComputeOp]
    # specify the source of the data, if absent, data must be passed at runtime manually
    source: t.Optional[Operator]
    # specify the sink to write the data to
    sink: t.Optional[Operator]
    # specify the alert to generate
    alert: t.Optional[Operator]
    # specify the plot to generate
    plot: t.Optional[Operator]

    def __init__(
        self,
        name: str,
        compute: list[ComputeOp],
        source: t.Optional[Operator] = None,
        sink: t.Optional[Operator] = None,
        alert: t.Optional[Operator] = None,
        plot: t.Optional[Operator] = None,
    ):
        self.name = name
        self.compute = compute
        self.source = source
        self.alert = alert
        self.sink = sink
        self.plot = plot

    def make_executor(self, settings: "Settings") -> "SimpleCheckExecutor":
        """Make an executor for this check."""
        return SimpleCheckExecutor(check=self, settings=settings)

    def dict(self) -> dict:
        """Serialize this check to a dict."""
        params = {
            "name": self.name,
            "compute": [
                {
                    "output_cols": op["output_cols"],
                    "operator": to_py_types(op["operator"]),
                }
                for op in self.compute
            ],
            "source": to_py_types(self.source),
            "sink": to_py_types(self.sink),
            "alert": to_py_types(self.alert),
            "plot": to_py_types(self.plot),
        }
        op_name = getattr(self.__class__, "_uptrain_op_name")
        return {"op_name": op_name, "params": params}

    @classmethod
    def from_dict(cls, data: dict) -> "SimpleCheck":
        """Deserialize a check from a dict."""
        data = data["params"]

        compute = []
        for elem in data["compute"]:
            compute.append(
                {
                    "output_cols": elem["output_cols"],
                    "operator": deserialize_operator(elem["operator"]),
                }
            )

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
            alert=get_value("alert"),
            plot=get_value("plot"),
        )


class SimpleCheckExecutor:
    """Executor for a check."""

    op: SimpleCheck
    exec_source: t.Optional[OperatorExecutor]
    exec_compute: list[ComputeOpExec]
    exec_sink: t.Optional[OperatorExecutor]
    exec_alert: t.Optional[OperatorExecutor]

    def __init__(self, check: SimpleCheck, settings: "Settings"):
        self.op = check
        self.exec_source = (
            check.source.make_executor(settings) if check.source else None
        )
        self.exec_sink = check.sink.make_executor(settings) if check.sink else None
        self.exec_alert = check.alert.make_executor(settings) if check.alert else None
        self.exec_compute = [
            {
                "output_cols": op["output_cols"],
                "operator": op["operator"].make_executor(settings),
            }
            for op in check.compute
        ]
        # no need to make an executor for the plot, since it's not run at runtime

    def run(self, data: t.Optional[pl.DataFrame] = None) -> t.Optional[pl.DataFrame]:
        """Run this check on the given data."""
        # run the source if specified else use the provided data
        if self.exec_source is not None:
            res = self.exec_source.run()  # type: ignore
            data = res["output"]
        else:
            assert (
                data is not None
            ), "No source provided for this check, so data must be provided manually."

        # run the compute operations in sequence, passing the output of one to the next
        for compute_op in self.exec_compute:
            op = compute_op["operator"]
            col_names = compute_op["output_cols"]

            res = op.run(data)
            assert isinstance(res["output"], pl.DataFrame)
            rename_mapping = {
                get_output_col_name_at(i): name for i, name in enumerate(col_names)
            }
            data = res["output"].rename(rename_mapping)

        # run the sink
        if self.exec_sink is not None:
            self.exec_sink.run(data)

        # run the alert
        if self.exec_alert is not None:
            self.exec_alert.run(data)

        return data


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
        if os.path.exists(self.settings.logs_folder):
            # TODO: Do we need to clear this? It was deleting input and output files for the experiment?
            dummy = 1
            # clear_directory(self.settings.logs_folder)
        else:
            os.makedirs(self.settings.logs_folder)
        self.serialize()

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
