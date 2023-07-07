"""This example shows how to use the Uptrain client to schedule an eval run 
on the Uptrain platform. 

The dataset comes from a QnA task where the objective is to answer a question, 
given some context obtained from doing an embedding search on a corpus of documents. 
"""

from uptrain.framework import CheckSet, Settings, Check
from uptrain.operators.io import JsonReader
from uptrain.operators import (
    UMAP,
    CosineSimilarity,
    Distribution,
    PlotlyChart,
)
from uptrain.operators.language import (
    RougeScore,
)


# Create the check-set object that lists the checks to run
def get_list_checks():
    check_1 = Check(
        name="scores",
        operators=[
            RougeScore(
                score_type="precision",
                col_in_generated="response",
                col_in_source="document_text",
            ),
            CosineSimilarity(
                col_in_vector_1="question_embeddings",
                col_in_vector_2="response_embeddings",
            ),
        ],
        plots=[PlotlyChart.Table(title="All scores")],
    )
    check_2 = Check(
        name="question_umap",
        operators=[
            UMAP(
                col_in_embs_1="question_embeddings",
                col_in_embs_2="response_embeddings",
            )
        ],
        plots=[
            PlotlyChart.Scatter(
                title="UMAP for question embeddings",
                props=dict(x="umap_0", y="umap_1", symbol="symbol", color="cluster"),
            )
        ],
    )
    check_3 = Check(
        name="distribution-embeddings",
        operators=[
            Distribution(
                kind="cosine_similarity",
                col_in_embs=["context_embeddings", "response_embeddings"],
                col_in_groupby=["question_idx", "experiment_id"],
                col_out=["similarity-context", "similarity-response"],
            )
        ],
        plots=[
            PlotlyChart.Histogram(
                title="Embeddings similarity - Context",
                props=dict(x="similarity-context", nbins=20),
            ),
            PlotlyChart.Histogram(
                title="Embeddings similarity - Responses",
                props=dict(x="similarity-response", nbins=20),
            ),
        ],
    )

    return [check_1, check_2, check_3]


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
    resp = client.add_dataset("qna_docs_samples", dataset_path)
    print("Response from adding the dataset: ", resp)

    # adding the eval to the server
    resp = client.add_checkset("test_qna_docs", check_set)
    print("Response from adding the eval: ", resp)

    # scheduling a run for the eval
    resp = client.add_run(dataset="output_w_embs", checkset="test_docs")
    print("Response from adding the run: ", resp)
