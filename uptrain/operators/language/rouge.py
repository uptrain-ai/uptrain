"""
Implement checks to test if a piece of text has been taken from a source.

This module provides the `RougeScore` class, which allows comparing a generated text with a source text to check if it has been taken from the source. It uses the Rouge score metric, specifically the Rouge-L score, to measure the similarity between the two texts.

"""

from __future__ import annotations
import typing as t

from loguru import logger
import polars as pl
from uptrain.framework import Settings

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.utilities import lazy_load_dep

rouge_scorer = lazy_load_dep("rouge_score.rouge_scorer", "rouge_score")


@register_op
class RougeScore(ColumnOp):
    """
    Operator to compare a generated text with a source text using the Rouge score metric.

    Attributes:
        score_type (Literal["precision", "recall", "f1"]): The type of Rouge score to calculate.
        col_in_generated (str): The name of the input column containing the generated text.
        col_in_source (str): The name of the input column containing the source text.
        col_out (str): The name of the output column containing the Rouge scores.

    Returns:
        dict: A dictionary containing the Rouge scores for each pair of generated and source text.

    Example:
        ```
        import polars as pl
        from uptrain.operators import RougeScore

        # Create a DataFrame
        df = pl.DataFrame({
            "text_generated": ["This is the generated text.", "Another generated sentence."],
            "text_source": ["This is the original source text.", "This is a different source text."]
        })

        # Create an instance of the RougeScore class
        rouge_op = RougeScore(score_type="f1")

        # Calculate the Rouge-L scores
        scores = rouge_op.run(df)["output"]

        # Print the Rouge-L scores
        print(scores)
        ```

    Output:
        ```
        shape: (2,)
        Series: '_col_0' [i64]
        [
                72
                0
        ]
        ```

    """

    score_type: t.Literal["precision", "recall", "f1"]
    col_in_generated: str = "text_generated"
    col_in_source: str = "text_source"
    col_out: str = "rouge_score"

    def setup(self, settings: Settings):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        text_generated = data.get_column(self.col_in_generated)
        text_source = data.get_column(self.col_in_source)

        results = []
        scores = []
        for i in range(len(text_generated)):
            scorer = rouge_scorer.RougeScorer(["rougeL"])  # type: ignore
            if text_source[i] is None or text_generated[i] is None:
                scores.append({"rougeL": (0, 0, 0)})
            else:
                scores.append(scorer.score(text_source[i], text_generated[i]))

        type_to_index = {"precision": 0, "recall": 1, "f1": 2}
        if self.score_type not in type_to_index:
            raise Exception(f"{self.score_type} not implemented")
        else:
            score_index = type_to_index[self.score_type]

        results = pl.Series([int(x["rougeL"][score_index] * 100) for x in scores])
        return {"output": data.with_columns([results.alias(self.col_out)])}
