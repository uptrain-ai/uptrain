"""
Implement checks to test if a piece of text has been taken from a source.

This module provides the `BLEUScore` class, which allows comparing a generated text with a source text to check if it has been taken from the source. It uses the BLEU score metric, specifically the BLEU score, to measure the similarity between the two texts.

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

# blue_score = lazy_load_dep("nltk.translate.bleu_score", "nltk")
torchmetircs_text = lazy_load_dep("torchmetrics.functional.text", "torchmetrics")


@register_op
class BLEUScore(ColumnOp):
    """
    Operator to compare a generated text with a source text using the BLEU score metric.
    More about BLEU - https://en.wikipedia.org/wiki/BLEU

    Attributes:
        col_in_generated (str): The name of the input column containing the generated text.
        col_in_source (str): The name of the input column containing the source text.
        col_out (str): The name of the output column containing the BLEU scores.

    Returns:
        dict: A dictionary containing the BLEU scores for each pair of generated and source text.

    Example:
        ```
        import polars as pl
        from uptrain.operators import BLEUScore

        # Create a DataFrame
        df = pl.DataFrame({
            "text_generated": ["This is the generated text.", "Another generated sentence."],
            "text_source": ["This is the original source text.", "This is a different source text."]
        })

        # Create an instance of the BLEUScore class
        bleu_op = BLEUScore()

        # Calculate the BLEU scores
        scores = bleu_op.run(df)["output"]

        # Print the BLEU scores
        print(scores["bleu_score"])
        ```

    Output:
        ```
        shape: (2,)
        Series: 'bleu_score' [i64]
        [
            65
            0
        ])
        ```

    """

    col_in_generated: str = "text_generated"
    col_in_source: str = "text_source"
    col_out: str = "bleu_score"

    def setup(self, settings: Settings):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        text_generated = data.get_column(self.col_in_generated)  # candidate/preds
        text_source = data.get_column(self.col_in_source)  # reference/target

        results = []
        scores = []
        for i in range(len(text_generated)):
            # scorer = blue_score.sentence_bleu  # type: ignore
            scorer = torchmetircs_text.bleu_score
            if text_source[i] is None or text_generated[i] is None:
                scores.append({"bleu": 0})
            else:
                # scores.append({"bleu": scorer(references=[text_source[i].split()], hypothesis=text_generated[i].split(), weights=(1,0,0,0))})
                preds = text_generated[i]
                target = [text_source[i]]
                scores.append(
                    {"bleu": scorer(preds, target, n_gram=1).item()}
                )  # Same as nltk's blue_score with weights (1,0,0,0)

        results = pl.Series([int(x["bleu"] * 100) for x in scores])
        return {"output": data.with_columns([results.alias(self.col_out)])}
