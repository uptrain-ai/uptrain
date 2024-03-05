"""
Implement operators to do vector-search and retrieval documents for a given user query. 
"""

from __future__ import annotations
import typing as t
import copy

import numpy as np
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import (
    TransformOp,
    register_op,
    TYPE_TABLE_OUTPUT,
)
from uptrain.operators.embedding.embedding import Embedding
from uptrain.operators.io.base import JsonReader, CsvReader
from uptrain.utilities import lazy_load_dep, polars_to_pandas

faiss = lazy_load_dep("faiss", "faiss")


@register_op
class VectorSearch(TransformOp):
    """

     Attributes:
        col_in_query (str): Column name for the input query to be used for retrieval
        documents (str): List of documents for vector database.
        embeddings_model (str): Name of the embeddings model
        col_out (str): Column name for the retrieved_context
        top_k (int): Top K documents will be retrieved.
        distance_metric (str): One of ['cosine_similarity', 'l2_distance']
    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_in_query: str = "question"
    documents: t.Union[list[str], str, JsonReader, CsvReader] = None
    embeddings_model: str = ""
    col_out: str = "context"
    top_k: int = 1
    col_in_document: str = ""
    distance_metric: str = t.Literal["cosine_similarity", "l2_distance"]
    embedding_batch_size: int = 128

    def setup(self, settings: t.Optional[Settings] = None):
        read_op = None
        if isinstance(self.documents, list):
            documents_table = pl.DataFrame({"document": self.documents})
        elif isinstance(self.documents, str):
            if self.documents[-5:] == ".json":
                read_op = JsonReader(fpath=self.documents)
            elif self.documents[-6:] == ".jsonl":
                read_op = JsonReader(fpath=self.documents)
            elif self.documents[-4:] == ".csv":
                read_op = CsvReader(fpath=self.documents)
            else:
                read_op = JsonReader(fpath=self.documents)
                # raise Exception("File formats other than jsonl and csv are not supported")
        elif isinstance(self.documents, JsonReader) or isinstance(
            self.documents, CsvReader
        ):
            read_op = self.documents
        else:
            raise Exception(f"{type(self.documents)} is not supported")

        if read_op is not None:
            documents_table = pl.DataFrame(
                {
                    "document": read_op.setup(settings).run()["output"][
                        self.col_in_document
                    ]
                }
            )

        documents_table = pl.DataFrame(polars_to_pandas(documents_table))

        emb_op = Embedding(
            model=self.embeddings_model,
            col_in_text="document",
            col_out="document_embeddings",
            batch_size=self.embedding_batch_size,
        )
        doc_embeddings = np.array(
            list(
                emb_op.setup(settings).run(documents_table)["output"][
                    "document_embeddings"
                ]
            )
        )

        self.documents_list = documents_table["document"]

        if self.distance_metric == "cosine_similarity":
            self.vectorstore = faiss.IndexFlatIP(len(doc_embeddings[0]))
        elif self.distance_metric == "l2_distance":
            self.vectorstore = faiss.IndexFlatL2(len(doc_embeddings[0]))
        else:
            raise Exception(f"{self.distance_metric} is not allowed")
        self.vectorstore.add(doc_embeddings)

        self._settings = settings
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        emb_op = Embedding(
            model=self.embeddings_model,
            col_in_text=self.col_in_query,
            col_out=self.col_in_query + "_embeddings",
        )
        query_emb_res = emb_op.setup(self._settings).run(data)["output"].to_dicts()

        res = []
        for emb_res in query_emb_res:
            this_retrieved_scores, this_retrieved_idxs = self.vectorstore.search(
                np.array([emb_res[self.col_in_query + "_embeddings"]]), self.top_k
            )
            this_retrieved_documents = [
                self.documents_list[int(x)] for x in this_retrieved_idxs[0]
            ]

            del emb_res[self.col_in_query + "_embeddings"]

            this_retriev_res = copy.deepcopy(emb_res)
            this_retriev_res = []
            for _ in range(len(this_retrieved_documents)):
                this_retriev_res.append(copy.deepcopy(emb_res))
            for jdx, row in enumerate(this_retriev_res):
                row.update(
                    {
                        self.col_out: this_retrieved_documents[jdx],
                        "retrieval_rank": jdx + 1,
                        "retrieval_similarity_score": this_retrieved_scores[0][jdx],
                    }
                )
            res.extend(this_retriev_res)

        return {"output": pl.DataFrame(res)}
