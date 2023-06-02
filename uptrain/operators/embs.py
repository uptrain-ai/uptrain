"""
Implement operators to compute metrics over embeddings. 
"""

from __future__ import annotations
import typing as t

from loguru import logger
from pydantic import BaseModel
import numpy as np
import polars as pl

try:
    import umap
except ImportError:
    umap = None

if t.TYPE_CHECKING:
    from uptrain.framework.config import *
from uptrain.operators.base import *
from uptrain.utilities import dependency_required
from rouge_score import rouge_scorer


__all__ = ["Distribution", "UMAP"]


class SchemaDistribution(BaseModel):
    col_embs: str
    col_groupby: list[str]


@register_op
class Distribution(BaseModel):
    kind: t.Literal["cosine_similarity", "rouge"]
    schema_data: SchemaDistribution

    def make_executor(self, settings: t.Optional[Settings] = None):
        return DistExecutor(self)


class DistExecutor(OperatorExecutor):
    op: Distribution

    def __init__(self, op: Distribution):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        agg_func: t.Callable
        if self.op.kind == "cosine_similarity":
            agg_func = get_cosine_sim_dist
        elif self.op.kind == "rouge":
            agg_func = get_rouge_score
        else:
            raise NotImplementedError("Only cosine similarity is supported for now.")

        output_agg_col_name = get_output_col_name_at(0)
        dist_df = data.groupby(
            self.op.schema_data.col_groupby, maintain_order=True
        ).agg(
            [
                pl.col(self.op.schema_data.col_embs)
                .apply(agg_func)
                .alias(output_agg_col_name)
            ]
        )
        dist_df = dist_df.explode(output_agg_col_name)
        return {"output": dist_df}


class SchemaUmap(BaseModel):
    col_embs: str
    col_embs2: str


@register_op
class UMAP(BaseModel):
    schema_data: SchemaUmap

    def make_executor(self, settings: t.Optional[Settings] = None):
        return UmapExecutor(self)


@dependency_required(umap, "umap")
class UmapExecutor(OperatorExecutor):
    op: UMAP

    def __init__(self, op: UMAP):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        embs = np.asarray(data[self.op.schema_data.col_embs].to_list())
        embs2 = np.asarray(data[self.op.schema_data.col_embs2].to_list())

        embs_list = list(embs)
        embs_list.extend(list(embs2))
        combined_embs = np.array(embs_list)
        symbols = ["star"] * len(embs) + ["circle"] * len(embs2)
        clusters = ["default"] * len(combined_embs)
        umap_output = umap.UMAP().fit_transform(combined_embs)
        return {
            "output": pl.DataFrame(
                {
                    "umap_0": pl.Series(values=umap_output[:, 0]),
                    "umap_1": pl.Series(values=umap_output[:, 1]),
                    "symbol": pl.Series(values=symbols),
                    "cluster": pl.Series(values=clusters),
                }
            )
        }


# -----------------------------------------------------------
# Utility routines
# -----------------------------------------------------------


def sample_pairs_from_values(n_values: int, n_pairs: int):
    indices_1 = np.random.choice(n_values, n_pairs)
    indices_2 = np.random.choice(n_values, n_pairs)
    invalid = indices_1 == indices_2
    indices_2[invalid] = (indices_2[invalid] + 1) % n_values
    return indices_1, indices_2


def get_cosine_sim_dist(col_vectors: pl.Series, num_pairs_per_group: int = 10):
    array_vectors = col_vectors.to_numpy()
    indices_1, indices_2 = sample_pairs_from_values(
        len(array_vectors), num_pairs_per_group
    )
    values = []
    for i1, i2 in zip(indices_1, indices_2):
        v1 = array_vectors[i1]
        v2 = array_vectors[i2]
        values.append(np.dot(v1, v2) / np.linalg.norm(v1) * np.linalg.norm(v2))
    return values


def get_rouge_score(col_vectors: pl.Series, num_pairs_per_group: int = 10):
    array_vectors = col_vectors.to_numpy()
    indices_1, indices_2 = sample_pairs_from_values(
        len(array_vectors), num_pairs_per_group
    )
    values = []
    for i1, i2 in zip(indices_1, indices_2):
        v1 = array_vectors[i1]
        v2 = array_vectors[i2]

        scorer = rouge_scorer.RougeScorer(["rougeL"])
        values.append(int(scorer.score(v1, v2)["rougeL"][2] * 100))
    return values
