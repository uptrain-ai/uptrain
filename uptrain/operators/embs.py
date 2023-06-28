"""
Implement operators to compute metrics over embeddings. 
"""

from __future__ import annotations
import typing as t

from loguru import logger
import numpy as np
import polars as pl
from pydantic import root_validator

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.utilities import lazy_load_dep

umap = lazy_load_dep("umap", "umap-learn")
rouge_scorer = lazy_load_dep("rouge_score.rouge_scorer", "rouge_score")


@register_op
class Distribution(TableOp):
    kind: t.Literal["cosine_similarity", "rouge"]
    col_in_embs: list[str]
    col_in_groupby: list[str]
    col_out: list[str] | None = None
    _agg_func: t.Callable | None = None

    @root_validator(pre=True)
    def check_cols(cls, values):
        if values["col_out"] is not None:
            assert len(values["col_out"]) == len(
                values["col_in_embs"]
            ), "Distribution Op needs as many output columns as input embedding columns"
        return values

    def setup(self, settings: t.Optional[Settings] = None):
        if self.kind == "cosine_similarity":
            self._agg_func = get_cosine_sim_dist
        elif self.kind == "rouge":
            self._agg_func = get_rouge_score
        else:
            raise NotImplementedError(
                f"Similarity metric: {self.kind} not supported for now."
            )
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        if self.col_out is None:
            agg_cols = [get_output_col_name_at(i) for i in range(len(self.col_in_embs))]
        else:
            agg_cols = self.col_out

        dist_df = (
            data.groupby(self.col_in_groupby, maintain_order=True)
            .agg(
                [
                    pl.col(_col_in).apply(self._agg_func).alias(_col_out)
                    for _col_in, _col_out in zip(self.col_in_embs, agg_cols)
                ]
            )
            .explode(agg_cols)
        )
        return {"output": dist_df}


@register_op
class UMAP(TableOp):
    col_in_embs: str
    col_in_embs2: str

    def setup(self, _: t.Optional[Settings] = None):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        embs = np.asarray(data[self.col_in_embs].to_list())
        embs2 = np.asarray(data[self.col_in_embs2].to_list())

        embs_list = list(embs)
        embs_list.extend(list(embs2))
        combined_embs = np.array(embs_list)
        symbols = ["star"] * len(embs) + ["circle"] * len(embs2)
        clusters = ["default"] * len(combined_embs)
        umap_output = umap.UMAP().fit_transform(combined_embs)  # type: ignore
        return {
            "output": pl.DataFrame(
                [
                    pl.Series(values=umap_output[:, 0]).alias("umap_0"),
                    pl.Series(values=umap_output[:, 1]).alias("umap_1"),
                    pl.Series(values=symbols).alias("symbol"),
                    pl.Series(values=clusters).alias("cluster"),
                ]
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

        scorer = rouge_scorer.RougeScorer(["rougeL"])  # type: ignore
        values.append(int(scorer.score(v1, v2)["rougeL"][2] * 100))
    return values
