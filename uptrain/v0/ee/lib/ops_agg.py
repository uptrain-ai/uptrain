"""Operators to compute metrics over embeddings"""

from __future__ import annotations
import os
import uuid
from typing import Any, Callable, Literal, Union
from itertools import product
from functools import cache

import duckdb
import numba
import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
from pydantic import BaseModel

from .ops_base import (
    Operator,
    OperatorExecutor,
    arrow_batch_to_table,
    array_arrow_to_np,
    array_np_to_arrow,
    np_arrays_to_arrow_table,
    table_arrow_to_np_arrays,
)

PARTITION_COLUMN = "partition_index"

# -----------------------------------------------------------
# Window Aggregation Operators (N-to-N)
# -----------------------------------------------------------


class WindowAggOp(BaseModel):
    """Operator to compute a window aggregation over a column in a table (N-to-N)."""

    value_col: str  # the column to aggregate over in each group
    seq_col: str  # the column to sort by before aggregation


@ray.remote
class WindowAggExecutor(OperatorExecutor):
    """Executor for window aggregations."""

    op: WindowAggOp
    cache_conn: duckdb.DuckDBPyConnection
    compute_loop: Callable

    def __init__(self, op: WindowAggOp, compute_op: Callable) -> None:
        """Initialize a Ray actor for the given operator.

        Args:
            op: Operator to execute.
            compute_op: Function to computes the aggregate value for the given value and intermediate value.
                The executor batches calls to this function and jit compiles the loop using numba.
        """
        self.op = op
        self.compute_loop = generate_compute_loop_for_window_agg(compute_op)

        os.makedirs(".cache", exist_ok=True)
        self.cache_conn = duckdb.connect(f".cache/{uuid.uuid4()}.duckdb")
        self.cache_conn.execute(
            f"CREATE TABLE interm_state (id STRING PRIMARY KEY, value FLOAT[]);"
        )  # TODO: support other types?

    def fetch_interm_state(self, tbl: pa.Table) -> pa.Table:
        """Fetches the intermediate state for the ids in the given table already seen by this operator,
        and selects the first value for each id not seen yet.
        """
        self.cache_conn.execute(
            """
            SELECT * FROM (
                SELECT id, value
                FROM interm_state
                WHERE id IN (SELECT {id_col} from tbl)
                
                UNION
            
                SELECT {id_col}, FIRST({value_col} ORDER BY {seq_col} ASC)
                FROM tbl 
                WHERE {id_col} NOT IN (SELECT id FROM interm_state)
                GROUP BY {id_col}
            )
            ORDER BY 1 ASC;
            """.format(
                id_col=PARTITION_COLUMN,
                value_col=self.op.value_col,
                seq_col=self.op.seq_col,
            )
        )
        return self.cache_conn.fetch_arrow_table()

    def update_interm_state(self, id_array: pa.Array, value_array: pa.Array):
        tbl = pa.Table.from_arrays([id_array, value_array], ["id", "value"])

        # upserts don't work for List data types, so we gotta do the update in steps.
        self.cache_conn.execute(
            "DELETE FROM interm_state WHERE id IN (SELECT id FROM tbl);"
        )
        self.cache_conn.execute("INSERT INTO interm_state SELECT id, value FROM tbl;")

    def run(self, tbl: Union[pa.Table, pa.RecordBatch]) -> pa.Array:
        tbl = arrow_batch_to_table(tbl)

        # We assume the table is already sorted by the partition_id and seq_col.
        # Get count of rows for each key value. The agg operator can use it to figure out the partition boundaries.
        partition_counts = (
            tbl.group_by([PARTITION_COLUMN])
            .aggregate([(PARTITION_COLUMN, "count")])
            .sort_by([(PARTITION_COLUMN, "ascending")])
        )
        partition_counts_array = array_arrow_to_np(
            partition_counts[f"{PARTITION_COLUMN}_count"]
        )

        [value_array] = table_arrow_to_np_arrays(tbl, [self.op.value_col])
        interm_state_table = self.fetch_interm_state(tbl)
        interm_state_array = table_arrow_to_np_arrays(interm_state_table, ["value"])[0]

        assert len(partition_counts_array) == len(interm_state_array)
        output_value_array, new_interm_state_array = self.compute_loop(
            partition_counts_array, value_array, interm_state_array
        )
        self.update_interm_state(
            interm_state_table["id"], array_np_to_arrow(new_interm_state_array)
        )
        return array_np_to_arrow(output_value_array)


def compute_op_l2dist_initial(
    value: np.ndarray, interm_value: np.ndarray
) -> tuple[np.floating, np.ndarray]:
    return np.sum(np.square(value - interm_value)), interm_value  # type: ignore


def compute_op_l2dist_running(
    value: np.ndarray, interm_value: np.ndarray
) -> tuple[np.floating, np.ndarray]:
    return np.sum(np.square(value - interm_value)), value  # type: ignore


def compute_op_cosine_dist_initial(
    value: np.ndarray, interm_value: np.ndarray
) -> tuple[np.floating, np.ndarray]:
    cos_similarity = np.dot(value, interm_value) / (
        np.linalg.norm(value) * np.linalg.norm(interm_value)
    )
    return (1 - cos_similarity), interm_value


def compute_op_cosine_dist_running(
    value: np.ndarray, interm_value: np.ndarray
) -> tuple[np.floating, np.ndarray]:
    cos_similarity = np.dot(value, interm_value) / (
        np.linalg.norm(value) * np.linalg.norm(interm_value)
    )
    return (1 - cos_similarity), value


def compute_op_norm_ratio_initial(
    value: np.ndarray, interm_value: np.ndarray
) -> tuple[np.floating, np.ndarray]:
    ratio = np.linalg.norm(value) / max(np.linalg.norm(interm_value), 1e-6)  # type: ignore
    return ratio, interm_value


def compute_op_norm_ratio_running(
    value: np.ndarray, interm_value: np.ndarray
) -> tuple[np.floating, np.ndarray]:
    ratio = np.linalg.norm(value) / max(np.linalg.norm(interm_value), 1e-6)  # type: ignore
    return ratio, value


@cache
def generate_compute_loop_for_window_agg(compute_fn: Callable) -> Callable:
    """Generates a compute loop for the given function."""

    inlined_fn = numba.njit(inline="always")(compute_fn)

    @numba.njit
    def compute_loop(partition_counts_array, value_array, interm_state_array):
        """Goes through the value array and computes the output value for each value, and updating the
        intermediate state.

        Args:
            partition_counts_array (np.ndarray): Array of counts of rows for each partition.
            value_array (np.ndarray): Array of values to compute the output for.
            interm_state_array (np.ndarray): Array of intermediate states for each partition.

        Returns:
            tuple[np.ndarray, np.ndarray]: The output value array and the new intermediate state array.
        """
        output_value_array = np.zeros(len(value_array))
        new_interm_state_array = np.zeros_like(interm_state_array)

        interm_idx = 0
        interm_state = interm_state_array[interm_idx]
        change_indices = np.cumsum(partition_counts_array)

        for idx, value in enumerate(value_array):
            if idx == change_indices[interm_idx]:
                # store interm state for the current partition, and move to the next
                new_interm_state_array[interm_idx] = interm_state
                interm_idx += 1
                interm_state = interm_state_array[interm_idx]
            output_value_array[idx], interm_state = inlined_fn(value, interm_state)  # type: ignore
        new_interm_state_array[interm_idx] = interm_state

        return output_value_array, new_interm_state_array

    return compute_loop


class L2Dist(WindowAggOp):
    """Computes the L2 distance between the current embedding and the initial/previous one."""

    mode: Literal["initial", "running"]

    def make_actor(self):
        # string casting to appease pylance since it doesn't let me compare a Literal to a string
        mode = str(self.mode)
        if mode == "initial":
            return WindowAggExecutor.remote(self, compute_op_l2dist_initial)
        elif mode == "running":
            return WindowAggExecutor.remote(self, compute_op_l2dist_running)
        else:
            raise ValueError(f"Unknown mode: {mode}")


class CosineDist(WindowAggOp):
    """Computes the cosine distance between the current embedding and the initial/previous one."""

    mode: Literal["initial", "running"]

    def make_actor(self):
        mode = str(self.mode)
        if mode == "initial":
            return WindowAggExecutor.remote(self, compute_op_cosine_dist_initial)
        elif mode == "running":
            return WindowAggExecutor.remote(self, compute_op_cosine_dist_running)
        else:
            raise ValueError(f"Unknown mode: {mode}")


class NormRatio(WindowAggOp):
    """Computes the ratio between the current embedding and the initial/previous one."""

    mode: Literal["initial", "running"]

    def make_actor(self):
        mode = str(self.mode)
        if mode == "initial":
            return WindowAggExecutor.remote(self, compute_op_norm_ratio_initial)
        elif mode == "running":
            return WindowAggExecutor.remote(self, compute_op_norm_ratio_running)
        else:
            raise ValueError(f"Unknown mode: {mode}")


# -----------------------------------------------------------
# Pairwise metrics computed over the full table at once (N-to-1)
# -----------------------------------------------------------


class ReduceOp(BaseModel):
    """Operators that produce a single row of output (N-to-1)."""

    value_col: str  # the column to aggregate over


class CosineDistHistogram(ReduceOp):
    """Computes the histogram of cosine distances between all embeddings in the table."""

    def make_actor(self):
        return PairwiseMetricExecutor.remote(self, compute_op_cosine_dist_initial)


@ray.remote
class PairwiseMetricExecutor:
    """Executor for computing a metric between pairs of embeddings."""

    op: ReduceOp
    compute_func: Callable

    def __init__(self, op: ReduceOp, compute_op: Callable) -> None:
        self.op = op
        self.compute_fn = compute_op


# -----------------------------------------------------------
# Partition Operator
# -----------------------------------------------------------


class PartitionOp(BaseModel, arbitrary_types_allowed=True):
    """Operator to partition a table/batch based on values in a set of columns,
    compute an aggregate on each partition, and combine the results.
    """

    columns: list[str]  # list of columns to partition on
    agg_ops: dict[
        str, Operator
    ]  # operators to apply to each partition, they must have the same n-arity

    def make_actor(self):
        return PartitionExecutor.remote(self)


@ray.remote
class PartitionExecutor:
    """Executor for partitioning."""

    op: PartitionOp
    agg_actors: list[OperatorExecutor]

    def __init__(self, op: PartitionOp) -> None:
        self.op = op
        self.agg_actors = [op.make_actor() for op in op.agg_ops.values()]

    def run(self, batch: Union[pa.Table, pa.RecordBatch]) -> pa.Table:
        if batch is None:
            return None
        tbl = arrow_batch_to_table(batch)

        # we don't know the primary key, so all aggregations must have the same sequence column so we can join back the outputs
        seq_cols = [op.seq_col for op in self.op.agg_ops.values()]  # type: ignore
        assert len(set(seq_cols)) == 1
        seq_col = seq_cols[0]

        # Create a column by concatenating the partition columns, and use it as the sort key so partitions are contiguous
        tbl = tbl.append_column(
            PARTITION_COLUMN,
            pc.binary_join_element_wise(  # type: ignore
                *[pc.cast(tbl[col], pa.string()) for col in self.op.columns], "_"
            ),
        ).sort_by([(PARTITION_COLUMN, "ascending"), (seq_col, "ascending")])

        result_refs = []
        for agg_op, agg_actor in zip(self.op.agg_ops.values(), self.agg_actors):
            assert isinstance(agg_op, WindowAggOp)
            tbl_input = tbl.select([PARTITION_COLUMN, agg_op.seq_col, agg_op.value_col])
            result_refs.append(agg_actor.run.remote(tbl_input))

        output_arrays = [arr for arr in ray.get(result_refs)]
        for op, arr in zip(self.op.agg_ops, output_arrays):
            tbl = tbl.append_column(op, arr)  # type: ignore
        return tbl
