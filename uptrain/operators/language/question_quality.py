"""
Implement operators to check the quality of the question given by the user. 
"""

from __future__ import annotations
import typing as t

from loguru import logger
import polars as pl


if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import register_op, ColumnOp, TYPE_TABLE_OUTPUT


@register_op
class ValidQuestionScore(ColumnOp):
    """
    Simply check the number of words in the question and grades as incomplete if below a threshold
    Attributes:
        col_question: (str) Column Name for the stored questions
        col_out: (str) Column
    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_question: str = "question"
    words_threshold: int = 1
    col_out: str = "score_valid_question"

    def setup(self, settings: t.Optional[Settings] = None):
        assert settings is not None
        self.settings = settings
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        data_send = data.to_dicts()
        results = []
        try:
            for row in data_send:
                question = row.pop(self.col_question)
                results.append(
                    {
                        "score_valid_question": int(
                            len(question.split(" ")) > self.words_threshold
                        )
                    }
                )
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ValidQuestionScore`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename({"score_valid_question": self.col_out})
            )
        }
