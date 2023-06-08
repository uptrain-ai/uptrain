import openai
import copy
import argparse

from uptrain.framework.config import Config, Settings, SimpleCheck
from uptrain.io import JsonReader, DeltaWriter, JsonWriter
from uptrain.operators import (
    PlotlyChart,
    Distribution,
    CosineSimilarity,
    UMAP
)

from uptrain.operators.language import (
    Embedding,
    RougeScore,
    DocsLinkVersion,
    TextLength,
    TextComparison,
    ModelGradeScore
)
from regression_testing.experiment import ExperimentManager


prompt_template = """
    You are a {persona} that can only quote text from documents. You will be given a section of technical documentation titled {document_title}, found at {document_link}. 
    The input is: '{question}?'. The input is a question, a problem statement, or a task. It is about one or many topics. 
    
    You are only allowed to quote sections of text.  
    
    Your task is to quote exactly all sections of the document that are relevant to any topics of the input. If there are code or examples, you must copy those sections too. Copy the text exactly as found in the original document. If you are copying a table, make sure you copy the table headers.
    
    Okay, here is the document:
    --- START: Document ---
    
    # Document title: {document_title}
    {document_text}

    -- END: Document ---
    Now do the task. You are only allowed to quote from the document. If there are no relevant sections, just respond with \"<EMPTY MESSAGE>\".
    
    DO NOT ATTEMPT TO ANSWER THE QUESTION OR PROBLEM. ONLY COPY. ONLY QUOTE.
    Here are the exact sections from the document:
"""

user_inputs = {
    "experiment_args": {
        "prompt_templates": [prompt_template],
        "model_names": ["gpt-3.5-turbo"],
        "comparison_args": [
            {
                "comparison_variables": "persona",
                "comparison_options": ["bot", "Streamlit expert", "developer"],
            }
        ],
    },
    "dataset_args": {
        "file_name": "",
        "input_variables": [
            "question",
            "document_title",
            "document_link",
            "document_text",
        ],
    },
    "evaluation_args": None,
}


def extract_version():
    return 1


def check_if_empty_response():
    return 1


LOGS_DIR = "examples/refactor/uptrain_logs"


def get_config():
    # Define the config
    checks = []

    # Compute all the embeddings - question, document, response
    checks.append(
        SimpleCheck(
            name="embeddings",
            compute=[
                Embedding(
                    col_in_text="question",
                    col_out="question_embeddings"
                ),
                Embedding(
                    col_in_text="document_text",
                    col_out="context_embeddings"
                ),
                Embedding(
                    col_in_text="response",
                    col_out="response_embeddings"
                ),
            ],
            source=JsonReader(fpath="{experiment_path}/output.jsonl"),
            sink=JsonWriter(fpath="{experiment_path}/interim_data/embeddings.jsonl"),
            plot=PlotlyChart(kind="table", title="Embeddings")
        )
    )

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
            source=JsonReader(fpath="{experiment_path}/interim_data/embeddings.jsonl"),
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
                    kind="rouge",
                    col_in_embs="document_text",
                    col_in_groupby=["question_idx", "experiment_id"],
                    col_out="document_text_rogue_f1",
                )
            ],
            source=JsonReader(fpath="{experiment_path}/interim_data/embeddings.jsonl"),
            plot=PlotlyChart(
                kind="histogram",
                title="Text Overlap between document embeddings",
                props=dict(x="document_text_rogue_f1", nbins=20, color="experiment_id"),
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
            source=JsonReader(fpath="{experiment_path}/output.jsonl"),
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
                    col_in_text="document_text",
                    col_out="document_context_length",
                )
            ],
            source=JsonReader(fpath="{experiment_path}/output.jsonl"),
            plot=PlotlyChart(
                kind="histogram",
                title="Bar Plot of Context Length",
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
            source=JsonReader(fpath="{experiment_path}/interim_data/embeddings.jsonl"),
            sink=JsonWriter(fpath="{experiment_path}/interim_data/a.jsonl"),
            plot=PlotlyChart(kind="table", title="Hallucination score"),
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
            source=JsonReader(fpath="{experiment_path}/interim_data/a.jsonl"),
            sink=JsonWriter(fpath="{experiment_path}/interim_data/b.jsonl"),        
            plot=PlotlyChart(
                kind="table", title="Similarity score between question and response"
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
            source=JsonReader(fpath="{experiment_path}/interim_data/embeddings.jsonl"),
            plot=PlotlyChart(
                kind="histogram",
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
            source=JsonReader(fpath="{experiment_path}/interim_data/b.jsonl"),
            sink=JsonWriter(fpath="{experiment_path}/interim_data/c.jsonl"),
            plot=PlotlyChart(
                kind="table", 
                title="Empty response occurence",
                pivot_args=[
                    {
                        "title": "Compare overall model scores",
                        "index": ["persona"],
                        "values": [
                            "response_document_overlap_score",
                            "similarity_score_between_question_and_extracted_text"
                            "is_empty_response"
                            ],
                        "columns": ["model"],
                        "aggfunc": "mean"                
                    },
                ]
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
            source=JsonReader(fpath="{experiment_path}/interim_data/embeddings.jsonl"),
            plot=PlotlyChart(
                kind="scatter",
                title="UMAP for question embeddings",
                props=dict(x="umap_0", y="umap_1", symbol="symbol", color="cluster"),
            ),
        )
    )

    checks.append(
        SimpleCheck(
            name="openai_grade",
            compute=[
                ModelGradeScore(
                    score_type="correct",
                    col_in_input="prompt",
                    col_in_completion="response",
                    col_out="chatgpt_model_grade_score",
                ),
            ],
            source=JsonReader(fpath="{experiment_path}/interim_data/c.jsonl"),
            plot=PlotlyChart(kind="table", title="ChatGPT graded score"),
        )
    )

    # checks.append(SimpleCheck(
    #     name="model_grading_correctness_score",
    #     compute=[
    #         {
    #             "output_cols": [],
    #             "operator": ""
    #         }
    #     ],
    #     source=JsonReader(fpath="{experiment_path}/output.jsonl"),
    #     plot=PlotlyChart(kind="table", title="Model Grading Correctness Score"),
    # ))

    cfg = {"checks": checks, "log_folder": LOGS_DIR}
    # cfg = Config(checks=checks, settings=Settings(logs_folder=LOGS_DIR))
    return cfg


# -----------------------------------------------------------
# Starting a streamlit server to visualize the results
# -----------------------------------------------------------


def start_streamlit():
    from uptrain.dashboard import StreamlitRunner

    runner = StreamlitRunner(LOGS_DIR)
    runner.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-streamlit", help="Boolean to start streamlit, True by default.", default=True, action="store_true")
    parser.add_argument("--file-name", type=str, help="The name of the file to load the dataset from.", required=True)
    args = parser.parse_args()
    
    user_inputs["dataset_args"]["file_name"] = args.file_name

    cfg = get_config()
    experiment_path = LOGS_DIR
    all_checks = copy.deepcopy(cfg["checks"])
    for check in all_checks:
        if check.source is not None:
            check.source.fpath = check.source.fpath.format(
                experiment_path=experiment_path
            )
        if check.sink is not None:
                check.sink.fpath = check.sink.fpath.format(experiment_path=experiment_path)
    cfg = Config(
        checks=all_checks,
        settings=Settings(logs_folder=LOGS_DIR),
    )
    openai.api_key = cfg.settings.openai_api_key
    cfg.setup()

    user_inputs["evaluation_args"] = {"checks": all_checks, "log_folder": experiment_path}
    manager = ExperimentManager(user_inputs)
    manager.run()
    
    for check in cfg.checks:
        results = check.make_executor(cfg.settings).run()

    if args.start_streamlit:
        start_streamlit()
