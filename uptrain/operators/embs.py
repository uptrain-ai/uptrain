"""
This module provides the following Distribution and UMAP operators that operate on embeddings:

Operators:
- `Distribution`: Computes the distribution of similarity metrics.
- `UMAP`: Performs UMAP dimensionality reduction.

NOTE: The above operators only take embeddings as input. Refer uptrain.operators.language.embedding to learn more.

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
class Distribution(TransformOp):
    """
    Operator for computing distribution of similarity metrics.

    Attributes:
        kind (Literal["cosine_similarity", "rouge"]): The type of similarity metric.
        col_in_embs (list[str]): The input columns containing embeddings.
        col_in_groupby (list[str]): The columns to group by.
        col_out (list[str] | None): The output columns. If None, automatically generated column names will be used.

    Raises:
        AssertionError: If the number of output columns does not match the number of input embedding columns.

    Example:
        ```
        import polars as pl
        from uptrain.operators import Distribution

        # Create an instance of the Distribution operator
        op = Distribution(
                kind="cosine_similarity",
                col_in_embs=["context_embeddings", "response_embeddings"],
                col_in_groupby=["question_idx", "experiment_id"],
                col_out=["similarity-context", "similarity-response"],
            )

        # Set up the operator
        op.setup()

        # Run the operator on the input data
        input_data = pl.DataFrame(...)
        output = op.run(input_data)["output"]

        # Print the output
        print(output)
        ```


    Output:
        ```
        shape: (90, 4)
        ┌──────────────┬───────────────┬────────────────────┬─────────────────────┐
        │ question_idx ┆ experiment_id ┆ similarity-context ┆ similarity-response │
        │ ---          ┆ ---           ┆ ---                ┆ ---                 │
        │ i64          ┆ i64           ┆ f64                ┆ f64                 │
        ╞══════════════╪═══════════════╪════════════════════╪═════════════════════╡
        │ 2            ┆ 0             ┆ 0.314787           ┆ 1.0                 │
        │ 2            ┆ 0             ┆ 0.387398           ┆ 0.204949            │
        │ 2            ┆ 0             ┆ 0.344797           ┆ 0.23195             │
        │ 2            ┆ 0             ┆ 0.306041           ┆ 1.0                 │
        │ …            ┆ …             ┆ …                  ┆ …                   │
        │ 0            ┆ 2             ┆ 0.997804           ┆ 0.996358            │
        │ 0            ┆ 2             ┆ 0.66862            ┆ 0.300155            │
        │ 0            ┆ 2             ┆ 0.224229           ┆ 0.637781            │
        │ 0            ┆ 2             ┆ 0.379936           ┆ 0.260659            │
        └──────────────┴───────────────┴────────────────────┴─────────────────────┘
        ```

    """

    kind: t.Literal["cosine_similarity", "rouge"]
    col_in_embs: list[str]
    col_in_groupby: list[str]
    col_out: list[str] | None = None

    @root_validator(pre=True)
    def _check_cols(cls, values):
        """
        Validator to check the validity of input and output column lists.

        Args:
            values (dict): The input attribute values.

        Returns:
            dict: The validated attribute values.

        Raises:
            AssertionError: If the number of output columns does not match the number of input embedding columns.

        """
        if values["col_out"] is not None:
            assert len(values["col_out"]) == len(
                values["col_in_embs"]
            ), "Distribution Op needs as many output columns as input embedding columns"
        return values

    def setup(self, settings: Settings):
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
class UMAP(ColumnOp):
    """
    Operator for performing UMAP dimensionality reduction.

    Attributes:
        col_in_embs (str): The input column containing embeddings.
        n_components (int): Number of components to keep.
        col_out (str): The umap column containing embeddings. 

    Example:
        ```
        import polars as pl
        from uptrain.operators import UMAP

        # Create an instance of the UMAP operator
        op = UMAP(
                col_in_embs="embedding",
                n_components=6,
                col_out= "umap_embedding"

            )

        # Set up the operator
        op.setup()

        # Run the operator on the input data
        input_data = pl.DataFrame(...)
        output = op.run(input_data)

        # Get the output DataFrame
        umap_df = output["output"]
        ```

    Output:
        ```
        shape: (2,)
        Series: '_col_0' [list[f32]]
        [
                [0.098575, 0.056978, … -0.071038]
                [0.072772, 0.073564, … -0.043947]
        ]
        ```

    """

    col_in_embs: str = 'embedding'
    n_components: int = 6
    col_out: str = 'umap_embedding' 

    def setup(self, settings: Settings):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        combined_embs = np.asarray(list(data[self.col_in_embs]))
        umap_output = umap.UMAP(n_components=self.n_components, metric='cosine', random_state=42).fit_transform(combined_embs)  # type: ignore
        umap_output = [[round(y, 8) for y in list(x)] for x in list(umap_output)]
        output_cols = [pl.Series(umap_output).alias(self.col_out)]
        output_cols.extend([pl.Series(np.array(umap_output)[:,idx]).alias(self.col_out + "_" + str(idx)) for idx in range(self.n_components)])

        return {
            "output": data.with_columns(output_cols)
        }


# -----------------------------------------------------------
# Utility routines (for above operators)
# -----------------------------------------------------------


def sample_pairs_from_values(n_values: int, n_pairs: int):
    """
    Sample pairs of indices from a given number of values.

    Args:
        n_values (int): The total number of values.
        n_pairs (int): The number of pairs to sample.

    Returns:
        Tuple[np.ndarray, np.ndarray]: The sampled pairs of indices.

    """
    indices_1 = np.random.choice(n_values, n_pairs)
    indices_2 = np.random.choice(n_values, n_pairs)
    invalid = indices_1 == indices_2
    indices_2[invalid] = (indices_2[invalid] + 1) % n_values
    return indices_1, indices_2


def get_cosine_sim_dist(col_vectors: pl.Series, num_pairs_per_group: int = 10):
    """
    Compute cosine similarity distances between pairs of vectors.

    Args:
        col_vectors (pl.Series): The column containing the vectors.
        num_pairs_per_group (int): The number of pairs to sample per group.

    Returns:
        List[float]: The computed cosine similarity distances.

    """
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
    """
    Compute ROUGE scores between pairs of vectors.

    Args:
        col_vectors (pl.Series): The column containing the vectors.
        num_pairs_per_group (int): The number of pairs to sample per group.

    Returns:
        List[int]: The computed ROUGE scores.

    """
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
