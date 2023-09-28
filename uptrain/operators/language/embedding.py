"""
Create embeddings for text

This module provides the `Embedding` class, which is used to generate embeddings for text using pre-trained models. 
The `Embedding` class supports different models such as MiniLM-L6-v2 and hkunlp/instructor-xl. The embeddings are 
generated for a specified text column in a DataFrame.

"""

from __future__ import annotations
import typing as t

from loguru import logger
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.utilities import lazy_load_dep

InstructorEmbedding = lazy_load_dep("InstructorEmbedding", "InstructorEmbedding")
sentence_transformers = lazy_load_dep("sentence_transformers", "sentence-transformers")


@register_op
class Embedding(ColumnOp):
    """
    Column operation that generates embeddings for text using pre-trained models.

    Attributes:
        model (Literal["MiniLM-L6-v2", "hkunlp/instructor-xl", "mpnet-base-v2"]): The name of the pre-trained model to use.
        col_in_text (str): The name of the text column in the DataFrame.
        col_out (str): The name of the output column in the DataFrame.

    Raises:
        Exception: If the specified model is not supported.

    Returns:
        TYPE_TABLE_OUTPUT: A dictionary containing the generated embeddings.

    Example:
        ```
        import polars as pl
        from uptrain.operators import Embedding

        # Create a DataFrame
        df = pl.DataFrame({
            "text": ["This is the first sentence.", "Here is another sentence."]
        })

        # Create an instance of the Embedding class
        embedding_op = Embedding(model="MiniLM-L6-v2", col_in_text="text", col_out="embedding")

        # Set up the Embedding operator
        embedding_op.setup()

        # Generate embeddings for the text column
        embeddings = embedding_op.run(df)["output"]

        # Print the embeddings
        print(embeddings)
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

    model: t.Literal["MiniLM-L6-v2", "hkunlp/instructor-xl", "mpnet-base-v2"]
    col_in_text: str = "text"
    col_out: str = "embedding"

    def setup(self, settings: Settings):
        if self.model == "hkunlp/instructor-xl":
            self._model_obj = InstructorEmbedding.INSTRUCTOR(self.model)  # type: ignore
        elif self.model == "MiniLM-L6-v2":
            self._model_obj = sentence_transformers.SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )  # type: ignore
        elif self.model == "mpnet-base-v2":
            self._model_obj = sentence_transformers.SentenceTransformer(
                "sentence-transformers/all-mpnet-base-v2"
            ) 
        else:
            raise Exception(f"Embeddings model: {self.model} is not supported yet.")
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        text = data.get_column(self.col_in_text)
        if self.model == "hkunlp/instructor-xl":
            inputs = [
                ["Represent the developer documentation sentence: ", x] for x in text
            ]
        elif self.model == "MiniLM-L6-v2" or self.model == "mpnet-base-v2":
            inputs = list(text)
        else:
            raise Exception("Embeddings model not supported")
        results = self._model_obj.encode(inputs)

        return {"output": data.with_columns([pl.Series(results).alias(self.col_out)])}
