"""
Implement checks to test if a piece of text has been taken from a source.

This module provides the `METEORScore` class, which allows comparing a generated text with a source text to check if it has been taken from the source. 
It uses the METEOR score metric, specifically the METEOR score, to measure the similarity between the two texts.
Metric for Evaluation of Translation with Explicit Ordering (METEOR) score is a metric that measures the quality 
of generated text based on the alignment between the generated text and the reference text. 

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

nltk = lazy_load_dep("nltk", "nltk")


@register_op
class METEORScore(ColumnOp):
    """
    Operator to compare a generated text with a source text using the METEOR score metric.
    More about METEOR - https://en.wikipedia.org/wiki/METEOR

    Attributes:
        col_in_generated (str): The name of the input column containing the generated text.
        col_in_source (str): The name of the input column containing the source text.
        col_out (str): The name of the output column containing the METEOR scores.

    Returns:
        dict: A dictionary containing the METEOR scores for each pair of generated and source text.

    Example:
        ```
        import polars as pl
        from uptrain.operators import METEORScore

        # Create a DataFrame
        df = pl.DataFrame({
            "text_generated": ["The cat was sat on the mat"],
            "text_source": ["The cat sat on the mat"]
        })

        # Create an instance of the METEORScore class
        METEOR_op = METEORScore()

        # Calculate the METEOR scores
        scores = METEOR_op.run(df)["output"]

        # Print the METEOR scores
        print(scores["METEOR_score"])
        ```

    Output:
        ```
        shape: (1,)
        Series: 'METEOR_score' [i64]
        [
            96
        ]
        ```

    """

    col_in_generated: str = "text_generated"
    col_in_source: str = "text_source"
    col_out: str = "METEOR_score"

    def setup(self, settings: Settings):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        text_generated = data.get_column(self.col_in_generated)  # candidate/preds
        text_source = data.get_column(self.col_in_source)  # reference/target

        results = []
        scores = []
        for i in range(len(text_generated)):
            scorer = nltk.translate.meteor
            if text_source[i] is None or text_generated[i] is None:
                scores.append({"METEOR": 0})
            else:
                preds = nltk.word_tokenize(text_generated[i])
                target = [nltk.word_tokenize(text_source[i])]
                scores.append({"METEOR": scorer(references=target, hypothesis=preds)})

        results = pl.Series([int(x["METEOR"] * 100) for x in scores])
        return {"output": data.with_columns([results.alias(self.col_out)])}
