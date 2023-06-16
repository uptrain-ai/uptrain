import os
from uptrain.framework import CheckSet, Settings, SimpleCheck
from uptrain.operators import (
    PlotlyChart,
    Distribution,
    CosineSimilarity,
    UMAP,
)
from uptrain.io import JsonReader, JsonWriter
from uptrain.operators.language import (
    Embedding,
    RougeScore,
    DocsLinkVersion,
    TextLength,
    TextComparison,
)

# Define the config
LOGS_DIR = "/tmp/uptrain_logs"


def produce_dataset_w_embs(source_path, sink_path):
    # Compute all the embeddings - question, document, response

    data = JsonReader(fpath=source_path).make_executor().run()["output"]
    ops = [
        Embedding(col_in_text="question", col_out="question_embeddings"),
        Embedding(col_in_text="document_text", col_out="context_embeddings"),
        Embedding(col_in_text="response", col_out="response_embeddings"),
    ]
    for op in ops:
        data = op.make_executor().run(data)["output"]

    os.remove(sink_path)
    JsonWriter(fpath=sink_path).make_executor().run(data)


def get_checkset(source_path):
    # Define the config
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
            name="text_overlap_between_documents",
            compute=[
                Distribution(
                    kind="rouge",
                    col_in_embs="document_text",
                    col_in_groupby=["question_idx", "experiment_id"],
                    col_out="document_text_rogue_f1",
                )
            ],
            plot=PlotlyChart.Histogram(
                title="Text Overlap between document embeddings",
                props=dict(x="document_text_rogue_f1", nbins=20),
            ),
        )
    )

    checks.append(
        SimpleCheck(
            name="document_link_version",
            compute=[
                DocsLinkVersion(
                    col_in_text="document_link",
                    col_out="document_link_version",
                )
            ],
            plot=PlotlyChart.Bar(
                title="Bar Plot of Link version",
                props=dict(x="document_link_version"),
            ),
        )
    )

    checks.append(
        SimpleCheck(
            name="document_context_length",
            compute=[
                TextLength(
                    col_in_text="document_text",
                    col_out="document_context_length",
                )
            ],
            plot=PlotlyChart.Histogram(
                title="Histogram of Context Length",
                props=dict(x="document_context_length", nbins=20),
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
            name="empty_response",
            compute=[
                TextComparison(
                    reference_text="<EMPTY MESSAGE>",
                    col_in_text="response",
                    col_out="is_empty_response",
                )
            ],
            plot=PlotlyChart.Table(title="Empty response occurence"),
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

    return CheckSet(
        source=JsonReader(fpath=source_path),
        checks=checks,
        settings=Settings(logs_folder=LOGS_DIR),
    )


# -----------------------------------------------------------
# Starting a streamlit server to visualize the results
# -----------------------------------------------------------


def start_streamlit():
    from uptrain.dashboard import StreamlitRunner

    runner = StreamlitRunner(LOGS_DIR)
    runner.start()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--start-streamlit", default=False, action="store_true")
    parser.add_argument(
        "--dataset-path",
        default="/home/ananis/repos/datasets/combined_output.jsonl",
        type=str,
    )
    args = parser.parse_args()

    DATASET_W_EMB_PATH = "/tmp/output_w_embs.jsonl"
    produce_dataset_w_embs(args.dataset_path, DATASET_W_EMB_PATH)

    cfg = get_checkset(DATASET_W_EMB_PATH)
    cfg.setup()
    cfg.run()

    if args.start_streamlit:
        start_streamlit()
