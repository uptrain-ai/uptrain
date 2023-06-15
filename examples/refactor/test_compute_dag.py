"""Assemble up a small DAG of operators and run it."""

import typing as t

from pydantic import BaseModel
import polars as pl

from uptrain.framework import Settings, OperatorDAG
from uptrain.operators.base import *


@register_op
class OpDouble(BaseModel):
    col_in: str
    col_out: str

    def make_executor(
        self, settings: t.Optional["Settings"] = None
    ) -> "OperatorExecutor":
        return OpDoubleExecutor(self, settings)


class OpDoubleExecutor(OperatorExecutor):
    def __init__(self, op: OpDouble, _: t.Optional["Settings"] = None):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        data = data.with_columns([(pl.col(self.op.col_in) * 2).alias(self.op.col_out)])
        return {"output": data}


@register_op
class OpTriple(BaseModel):
    col_in: str
    col_out: str

    def make_executor(
        self, settings: t.Optional["Settings"] = None
    ) -> "OperatorExecutor":
        return OpTripleExecutor(self, settings)


class OpTripleExecutor(OperatorExecutor):
    def __init__(self, op: OpTriple, _: t.Optional["Settings"] = None):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        data = data.with_columns([(pl.col(self.op.col_in) * 3).alias(self.op.col_out)])
        return {"output": data}


if __name__ == "__main__":
    dag = OperatorDAG("test")
    dag.add_step("A", OpDouble(col_in="col_1", col_out="col_A"))
    dag.add_step("B", OpTriple(col_in="col_1", col_out="col_B"))
    dag.add_step("C", OpTriple(col_in="col_A", col_out="col_C"), deps=["A"])

    print("Operator DAG:")
    print(dag)
    data = pl.DataFrame({"col_1": [1, 2, 3]})
    settings = Settings()
    output = dag.run(
        settings, node_inputs={"A": data, "B": data}, output_nodes=["B", "C"]
    )
    print("output for node B", output["B"])
    print("output for node C", output["C"])
