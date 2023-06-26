"""This example shows how to use the Uptrain client to schedule an eval run 
on the Uptrain platform. 

The dataset comes from a QnA task where the objective is to answer a question, 
given some context obtained from doing an embedding search on a corpus of documents. 
"""

from uptrain.framework import CheckSet, Settings, SimpleCheck
from uptrain.io import JsonReader
from uptrain.operators import UMAP, CosineSimilarity, Distribution, PlotlyChart
from uptrain.operators.language import (
    RougeScore,
)


# Create the check-set object that lists the checks to run
def get_list_checks():
    checks = []
    checks.append(
        SimpleCheck(
            name="distribution_of_document_embeddings",
            compute=[
                Distribution(
                    kind="cosine_similarity",
                    col_in_embs="context_embeddings",
                    col_in_groupby=["question_idx", "experiment_id"],
                    col_out="document_embeddings_cosine_distribution",
                )
            ],
            plot=PlotlyChart.Histogram(
                title="Distribution of document embeddings",
                props=dict(x="document_embeddings_cosine_distribution", nbins=20),
            ),
        )
    )
    checks.append(
        SimpleCheck(
            name="hallucination_check",
            compute=[
                RougeScore(
                    col_in_generated="response",
                    col_in_source="document_text",
                    col_out="response_document_overlap_score",
                )
            ],
            plot=PlotlyChart.Table(title="Hallucination score"),
        )
    )
    checks.append(
        SimpleCheck(
            name="semantic_similarity_between_question_and_extracted_text",
            compute=[
                CosineSimilarity(
                    col_in_vector_1="question_embeddings",
                    col_in_vector_2="response_embeddings",
                    col_out="similarity_score_between_question_and_extracted_text",
                ),
            ],
            plot=PlotlyChart.Table(
                title="Similarity score between question and response"
            ),
        )
    )
    checks.append(
        SimpleCheck(
            name="distribution_of_extracted_text_embeddings",
            compute=[
                Distribution(
                    kind="cosine_similarity",
                    col_in_embs="response_embeddings",
                    col_in_groupby=["question_idx", "experiment_id"],
                    col_out="extracted_text_embeddings_cosine_distribution",
                )
            ],
            plot=PlotlyChart.Histogram(
                title="Cosine Similarity between extracted text embeddings",
                props=dict(x="extracted_text_embeddings_cosine_distribution", nbins=20),
            ),
        )
    )
    checks.append(
        SimpleCheck(
            name="question_umap",
            compute=[
                UMAP(
                    col_in_embs="question_embeddings",
                    col_in_embs2="response_embeddings",
                )
            ],
            plot=PlotlyChart.Scatter(
                title="UMAP for question embeddings",
                props=dict(x="umap_0", y="umap_1", symbol="symbol", color="cluster"),
            ),
        )
    )
    return checks


if __name__ == "__main__":
    import os
    from uptrain.framework.remote import APIClient

    # Change the following to point point to your uptrain server
    uptrain_server_url = "http://localhost:4300/"
    uptrain_api_key = "test-key"
    dataset_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../datasets/qna_on_docs_samples.jsonl",
    )
    logs_dir = "/tmp/placeholder_logs"

    settings = Settings(
        logs_folder=logs_dir,
        uptrain_server_url=uptrain_server_url,
        uptrain_api_key=uptrain_api_key,
    )

    # NOTE: local file-system arguments like dataset paths and logs_folder are only relevant when testing
    # the eval locally. At the uptrain server, they are ignored.
    check_set = CheckSet(
        source=JsonReader(fpath=dataset_path),
        checks=get_list_checks(),
        settings=settings,
    )

    client = APIClient(settings=settings)
    # adding the dataset to the server
    resp = client.datasets.add("qna_docs_samples", dataset_path)
    print("Response from adding the dataset: ", resp)

    # adding the eval to the server
    resp = client.checksets.add("test_qna_docs", check_set)
    print("Response from adding the eval: ", resp)

    # scheduling a run for the eval
    resp = client.add_run(dataset="output_w_embs", checkset="test_docs")
    print("Response from adding the run: ", resp)
