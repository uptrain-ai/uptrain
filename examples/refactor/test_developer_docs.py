from uptrain.framework.config import Config, Settings, SimpleCheck
from uptrain.io import JsonReader, DeltaWriter
from uptrain.operators import GrammarScore, PlotlyChart
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
    'experiment_args': {
        "prompt_templates": [prompt_template],
        "model_names": ["gpt-3.5-turbo"],
        "comparison_args": [{
            "comparison_variables": 'persona',
            'comparison_options': ['bot', 'Streamlit expert', 'developer']
        }],
    },
    'dataset_args': {
        'file_name': "/Users/sourabhagrawal/Desktop/codes/llm/uptrain_experiments/uptrain/streamlit_new_small.jsonl",
        'input_variables': ['question', 'document_title', 'document_link', 'document_text'],
    },
    'evaluation_args': None
}


def extract_version():
    return 1

def check_if_empty_response():
    return 1

LOGS_DIR = "examples/refactor/uptrain_logs"

from uptrain.operators import Embeddings, Distribution, CustomCheck, TextLength, Rogue, CosineSimilarity, UMAP
def get_config():
    # Define the config
    checks = []

    # Compute all the embeddings - question, document, response
    checks.append(SimpleCheck(
        name="embeddings",
        compute=[
            {
                "output_cols": ["question_embeddings"],
                "operator": Embeddings(schema_data={"col_text": "question"}),
            },
            {
                "output_cols": ["context_embeddings"],
                "operator": Embeddings(schema_data={"col_text": "document_text"}),
            },
            {
                "output_cols": ["response_embeddings"],
                "operator": Embeddings(schema_data={"col_text": "response"}),
            },
        ],
        source=JsonReader(fpath="{experiment_path}/output.jsonl"),
        sink=DeltaWriter(fpath="{experiment_path}/interim_data/embeddings")
    ))

    checks.append(SimpleCheck(
        name="distribution_of_document_embeddings",
        compute=[
            {
                "output_cols": [],
                "operator": Distribution(schema_data={"col_text": "context_embeddings", "aggregate_col": "question_idx"}, operation="cosine_similarity"),
            }
        ],
        source=JsonReader(fpath="{experiment_path}/interim_data/embeddings"),
        plot=PlotlyChart(kind="histogram", title="Distribution of document embeddings"),
    ))

    checks.append(SimpleCheck(
        name="text_overlap_between_document_embeddings",
        compute=[
            {
                "output_cols": [],
                "operator": Distribution(schema_data={"col_text": "context_embeddings", "aggregate_col": "question_idx"}, operation="rogue"),
            }
        ],
        source=JsonReader(fpath="{experiment_path}/interim_data/embeddings"),
        plot=PlotlyChart(kind="histogram", title="Text Overlap between document embeddings"),
    ))

    checks.append(SimpleCheck(
        name="document_link_version",
        compute=[
            {
                "output_cols": ["document_link_version"],
                "operator": extract_version()
            }
        ],
        source=JsonReader(fpath="{experiment_path}/output.jsonl"),
        plot=PlotlyChart(kind="bar", title="Bar Plot of Link version"),
    ))

    checks.append(SimpleCheck(
        name="document_context_length",
        compute=[
            {
                "output_cols": ["document_context_length"],
                "operator": TextLength(schema_data={"col_text": "document_text"})
            }
        ],
        source=JsonReader(fpath="{experiment_path}/output.jsonl"),
        plot=PlotlyChart(kind="bar", title="Bar Plot of Context Length"),
    ))

    checks.append(SimpleCheck(
        name="hallucination_check",
        compute=[
            {
                "output_cols": ["overlap_score"],
                "operator": Rogue(schema_data={"col_1": "document_text", "col_2": "response"})
            }
        ],
        source=JsonReader(fpath="{experiment_path}/output.jsonl"),
        plot=PlotlyChart(kind="table", title="Hallucination score"),
    ))

    checks.append(SimpleCheck(
        name="semantic_similarity_between_question_and_extracted_text",
        compute=[
            {
                "output_cols": ["similarity_score_between_question_and_extracted_text"],
                "operator": CosineSimilarity(schema_data={"col_1": "question_embeddings", "col_2": "response_embeddings"})
            }
        ],
        source=JsonReader(fpath="{experiment_path}/interim_data/embeddings"),
        plot=PlotlyChart(kind="table", title="Hallucination score"),
    ))

    checks.append(SimpleCheck(
        name="distribution_of_extracted_text_embeddings",
        compute=[
            {
                "output_cols": [],
                "operator": Distribution(schema_data={"col_text": "response_embeddings", "aggregate_col": "question_idx"}, operation="cosine_similarity"),
            }
        ],
        source=JsonReader(fpath="{experiment_path}/interim_data/embeddings"),
        plot=PlotlyChart(kind="histogram", title="Cosine Similarity between extracted text embeddings"),
    ))

    checks.append(SimpleCheck(
        name="empty_response",
        compute=[
            {
                "output_cols": ["is_empty_response"],
                "operator": check_if_empty_response()
            }
        ],
        source=JsonReader(fpath="{experiment_path}/output.jsonl"),
        plot=PlotlyChart(kind="table", title="Empty response occurence"),
    ))

    checks.append(SimpleCheck(
        name="question_umap",
        compute=[
            {
                "output_cols": [],
                "operator": UMAP(schema_data={"col_text": "question_embeddings"})
            }
        ],
        source=JsonReader(fpath="{experiment_path}/interim_data/embeddings"),
        plot=PlotlyChart(kind="scatter", title="UMAP for question embeddings"),
    ))

    checks.append(SimpleCheck(
        name="model_grading_correctness_score",
        compute=[
            {
                "output_cols": [],
                "operator": ""
            }
        ],
        source=JsonReader(fpath="{experiment_path}/output.jsonl"),
        plot=PlotlyChart(kind="table", title="Model Grading Correctness Score"),
    ))

    # import os
    # import shutil
    # if os.path.exists(LOGS_DIR):
    #     shutil.rmtree(LOGS_DIR)

    cfg = {'checks': checks, 'log_folder': LOGS_DIR}
    # cfg = Config(checks=checks, settings=Settings(logs_folder=LOGS_DIR))
    return cfg

    # Execute the config
    cfg.setup()
    for check in cfg.checks:
        results = check.make_executor(cfg.settings).run()


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

    user_inputs['evaluation_args'] = get_config()
    manager = ExperimentManager(user_inputs)
    manager.run()

    if args.start_streamlit:
        start_streamlit()