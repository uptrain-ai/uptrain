import os
from uptrain.framework import CheckSet, Settings, SimpleCheck
from uptrain.operators import (
    PlotlyChart,
    Distribution,
    CosineSimilarity,
    UMAP,
    SelectOp,
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


# def produce_dataset_w_embs(source_path, sink_path):
#     # Compute all the embeddings - question, document, response

#     source = JsonReader(fpath=source_path)
#     source.setup()
#     data = source.run()["output"]

#     op = SelectOp(
#         columns={
#             "question_embeddings": Embedding(col_in_text="question"),
#             "context_embeddings": Embedding(col_in_text="document_text"),
#             "response_embeddings": Embedding(col_in_text="response"),
#         }
#     )
#     op.setup(Settings())
#     data = op.run(data)["output"]

#     os.remove(sink_path)
#     JsonWriter(fpath=sink_path).run(data)


def get_checkset(source_path):
    # Define the config
    checks = []

    checks.append(
        SimpleCheck(
            name="distribution_of_document_embeddings",
            sequence=[
                Distribution(
                    kind="cosine_similarity",
                    col_in_embs=["context_embeddings", "response_embeddings"],
                    col_in_groupby=["question_idx", "experiment_id"],
                    col_out=["similarity-context", "similarity-response"],
                )
            ],
            plot=[
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
    )

    checks.append(
        SimpleCheck(
            name="text_overlap_between_documents",
            sequence=[
                Distribution(
                    kind="rouge",
                    col_in_embs=["document_text"],
                    col_in_groupby=["question_idx", "experiment_id"],
                    col_out=["rogue_f1"],
                )
            ],
            plot=[
                PlotlyChart.Histogram(
                    title="Text Overlap between document embeddings",
                    props=dict(x="rogue_f1", nbins=20),
                )
            ],
        )
    )

    checks.append(
        SimpleCheck(
            name="quality_scores",
            sequence=[
                SelectOp(
                    columns={
                        "document_link_version": DocsLinkVersion(
                            col_in_text="document_link"
                        ),
                        "document_context_length": TextLength(
                            col_in_text="document_text"
                        ),
                        "response_document_overlap_score": RougeScore(
                            col_in_generated="response",
                            col_in_source="document_text",
                        ),
                        "question_response_similarity": CosineSimilarity(
                            col_in_vector_1="question_embeddings",
                            col_in_vector_2="response_embeddings",
                        ),
                        "empty_response": TextComparison(
                            reference_text="<EMPTY MESSAGE>",
                            col_in_text="response",
                        ),
                    }
                )
            ],
            plot=[
                PlotlyChart.Table(title="Quality scores"),
                PlotlyChart.Bar(
                    title="Bar Plot of Link version",
                    props=dict(x="document_link_version"),
                ),
                PlotlyChart.Histogram(
                    title="Histogram of Context Length",
                    props=dict(x="document_context_length", nbins=20),
                ),
            ],
        )
    )

    checks.append(
        SimpleCheck(
            name="question_umap",
            sequence=[
                UMAP(
                    col_in_embs="question_embeddings",
                    col_in_embs2="response_embeddings",
                )
            ],
            plot=[
                PlotlyChart.Scatter(
                    title="UMAP for question embeddings",
                    props=dict(
                        x="umap_0", y="umap_1", symbol="symbol", color="cluster"
                    ),
                )
            ],
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
    args = parser.parse_args()

    # produce_dataset_w_embs(args.dataset_path, DATASET_W_EMB_PATH)
    DATASET_W_EMB_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../datasets/qna_on_docs_samples.jsonl",
    )

    cfg = get_checkset(DATASET_W_EMB_PATH)
    cfg.setup()
    cfg.run()

    if args.start_streamlit:
        start_streamlit()
