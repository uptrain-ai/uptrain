from uptrain.framework.config import Config, Settings, SimpleCheck
from uptrain.io import JsonReader, DeltaWriter, JsonWriter
from uptrain.operators import (
    PlotlyChart,
    Distribution,
    CosineSimilarity,
    UMAP,
)
from uptrain.operators.language import (
    Embedding,
    RougeScore,
    DocsLinkVersion,
    TextLength,
    TextComparison,
)

# Define the config
LOGS_DIR = "/tmp/uptrain_logs"
DATASET_PATH = "/home/ananis/repos/datasets/combined_output.jsonl"
DATASET_W_EMB_PATH = "/home/ananis/repos/datasets/output_w_embs.jsonl"


def get_config():
    # Define the config
    checks = []

    # Compute all the embeddings - question, document, response
    checks.append(
        SimpleCheck(
            name="embeddings",
            compute=[
                Embedding(
                    dataschema={
                        "in_col_text": "question",
                        "out_col": "question_embeddings",
                    }
                ),
                Embedding(
                    dataschema={
                        "in_col_text": "document_text",
                        "out_col": "context_embeddings",
                    }
                ),
                Embedding(
                    dataschema={
                        "in_col_text": "response",
                        "out_col": "response_embeddings",
                    }
                ),
            ],
            source=JsonReader(fpath=DATASET_PATH),
            sink=JsonWriter(fpath=DATASET_W_EMB_PATH),
        )
    )

    checks.append(
        SimpleCheck(
            name="distribution_of_document_embeddings",
            compute=[
                Distribution(
                    dataschema={
                        "in_col_embs": "context_embeddings",
                        "in_col_groupby": ["question_idx", "experiment_id"],
                        "out_col": "document_embeddings_cosine_distribution",
                    },
                    kind="cosine_similarity",
                )
            ],
            source=JsonReader(fpath=DATASET_W_EMB_PATH),
            plot=PlotlyChart(
                kind="histogram",
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
                    dataschema={
                        "in_col_embs": "document_text",
                        "in_col_groupby": ["question_idx", "experiment_id"],
                        "out_col": "document_text_rogue_f1",
                    },
                    kind="rouge",
                )
            ],
            source=JsonReader(fpath=DATASET_W_EMB_PATH),
            plot=PlotlyChart(
                kind="histogram",
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
                    dataschema={
                        "in_col_text": "document_link",
                        "out_col": "document_link_version",
                    }
                )
            ],
            source=JsonReader(fpath=DATASET_W_EMB_PATH),
            plot=PlotlyChart(
                kind="bar",
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
                    dataschema={
                        "in_col_text": "document_text",
                        "out_col": "document_context_length",
                    }
                )
            ],
            source=JsonReader(fpath=DATASET_W_EMB_PATH),
            plot=PlotlyChart(
                kind="histogram",
                title="Histogram of Context Length",
                props=dict(x="document_context_length", nbins=20),
            ),
        )
    )

    # checks.append(
    #     SimpleCheck(
    #         name="hallucination_check",
    #         compute=[
    #             {
    #                 "output_cols": ["response_document_overlap_score"],
    #                 "operator": RougeScore(
    #                     dataschema={
    #                         "col_generated": "response",
    #                         "col_source": "document_text",
    #                     }
    #                 ),
    #             }
    #         ],
    #         source=JsonReader(fpath=DATASET_W_EMB_PATH),
    #         plot=PlotlyChart(kind="table", title="Hallucination score"),
    #     )
    # )

    # checks.append(
    #     SimpleCheck(
    #         name="semantic_similarity_between_question_and_extracted_text",
    #         compute=[
    #             {
    #                 "output_cols": [
    #                     "similarity_score_between_question_and_extracted_text"
    #                 ],
    #                 "operator": CosineSimilarity(
    #                     dataschema={
    #                         "col_vector_1": "question_embeddings",
    #                         "col_vector_2": "response_embeddings",
    #                     }
    #                 ),
    #             }
    #         ],
    #         source=JsonReader(fpath=DATASET_W_EMB_PATH),
    #         plot=PlotlyChart(
    #             kind="table", title="Similarity score between question and response"
    #         ),
    #     )
    # )

    # checks.append(
    #     SimpleCheck(
    #         name="distribution_of_extracted_text_embeddings",
    #         compute=[
    #             {
    #                 "output_cols": ["extracted_text_embeddings_cosine_distribution"],
    #                 "operator": Distribution(
    #                     dataschema={
    #                         "col_embs": "response_embeddings",
    #                         "col_groupby": ["question_idx", "experiment_id"],
    #                     },
    #                     kind="cosine_similarity",
    #                 ),
    #             }
    #         ],
    #         source=JsonReader(fpath=DATASET_W_EMB_PATH),
    #         plot=PlotlyChart(
    #             kind="histogram",
    #             title="Cosine Similarity between extracted text embeddings",
    #             props=dict(x="extracted_text_embeddings_cosine_distribution", nbins=20),
    #         ),
    #     )
    # )

    # checks.append(
    #     SimpleCheck(
    #         name="empty_response",
    #         compute=[
    #             {
    #                 "output_cols": ["is_empty_response"],
    #                 "operator": TextComparison(
    #                     dataschema={"col_text": "response"},
    #                     reference_text="<EMPTY MESSAGE>",
    #                 ),
    #             }
    #         ],
    #         source=JsonReader(fpath=DATASET_W_EMB_PATH),
    #         plot=PlotlyChart(kind="table", title="Empty response occurence"),
    #     )
    # )

    # checks.append(
    #     SimpleCheck(
    #         name="question_umap",
    #         compute=[
    #             {
    #                 "output_cols": [],
    #                 "operator": UMAP(
    #                     dataschema={
    #                         "col_embs": "question_embeddings",
    #                         "col_embs2": "response_embeddings",
    #                     }
    #                 ),
    #             }
    #         ],
    #         source=JsonReader(fpath=DATASET_W_EMB_PATH),
    #         plot=PlotlyChart(
    #             kind="scatter",
    #             title="UMAP for question embeddings",
    #             props=dict(x="umap_0", y="umap_1", symbol="symbol", color="cluster"),
    #         ),
    #     )
    # )

    return Config(checks=checks, settings=Settings(logs_folder=LOGS_DIR))


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

    cfg = get_config()
    cfg.setup()
    for check in cfg.checks:
        results = check.make_executor(cfg.settings).run()

    if args.start_streamlit:
        start_streamlit()
