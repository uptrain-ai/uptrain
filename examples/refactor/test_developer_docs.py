import openai
import copy

from uptrain.framework.config import Config, Settings, SimpleCheck
from uptrain.io import JsonReader, DeltaWriter, JsonWriter
from uptrain.operators import PlotlyChart, Embedding, RougeScore, Distribution, CosineSimilarity, DocsLinkVersion, UMAP, TextLength, TextComparison, ModelGradeScore
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

def get_config():
    # Define the config
    checks = []

    # Compute all the embeddings - question, document, response
    checks.append(SimpleCheck(
        name="embeddings",
        compute=[
            {
                "output_cols": ["question_embeddings"],
                "operator": Embedding(schema_data={"col_text": "question"}),
            },
            {
                "output_cols": ["context_embeddings"],
                "operator": Embedding(schema_data={"col_text": "document_text"}),
            },
            {
                "output_cols": ["response_embeddings"],
                "operator": Embedding(schema_data={"col_text": "response"}),
            },
        ],
        source=JsonReader(fpath="{experiment_path}/output.jsonl"),
        sink=JsonWriter(fpath="{experiment_path}/interim_data/embeddings.jsonl"),
        plot=PlotlyChart(kind="table", title="Embeddings")
    ))

    checks.append(SimpleCheck(
        name="distribution_of_document_embeddings",
        compute=[
            {
                "output_cols": ['document_embeddings_cosine_distribution'],
                "operator": Distribution(schema_data={"col_embs": "context_embeddings", "col_groupby": ["question_idx", "experiment_id"]}, kind="cosine_similarity"),
            }
        ],
        source=JsonReader(fpath="{experiment_path}/interim_data/embeddings.jsonl"),
        plot=PlotlyChart(kind="histogram", title="Distribution of document embeddings",
            props=dict(x="document_embeddings_cosine_distribution", nbins=20))
    ))

    checks.append(SimpleCheck(
        name="text_overlap_between_documents",
        compute=[
            {
                "output_cols": ['document_text_rogue_f1'],
                "operator": Distribution(schema_data={"col_embs": "document_text", "col_groupby": ["question_idx", "experiment_id"]}, kind="rouge"),
            }
        ],
        source=JsonReader(fpath="{experiment_path}/interim_data/embeddings.jsonl"),
        plot=PlotlyChart(kind="histogram", title="Text Overlap between document embeddings", 
                        props=dict(x="document_text_rogue_f1", nbins=20, color='experiment_id')),
    ))

    checks.append(SimpleCheck(
        name="document_link_version",
        compute=[
            {
                "output_cols": ["document_link_version"],
                "operator": DocsLinkVersion(schema_data={'col_text': 'document_link'})
            }
        ],
        source=JsonReader(fpath="{experiment_path}/output.jsonl"),
        plot=PlotlyChart(kind="bar", title="Bar Plot of Link version", props=dict(x='document_link_version')),
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
        plot=PlotlyChart(kind="histogram", title="Bar Plot of Context Length", props=dict(x='document_context_length', nbins=20, color='experiment_id')),
    ))

    checks.append(SimpleCheck(
        name="hallucination_check",
        compute=[
            {
                "output_cols": ["response_document_overlap_score"],
                "operator": RougeScore(schema_data={"col_generated": "response", "col_source": "document_text"})
            }
        ],
        source=JsonReader(fpath="{experiment_path}/interim_data/embeddings.jsonl"),
        sink=JsonWriter(fpath="{experiment_path}/interim_data/a.jsonl"),
        plot=PlotlyChart(kind="table", title="Hallucination score"),
    ))

    checks.append(SimpleCheck(
        name="semantic_similarity_between_question_and_extracted_text",
        compute=[
            {
                "output_cols": ["similarity_score_between_question_and_extracted_text"],
                "operator": CosineSimilarity(schema_data={"col_vector_1": "question_embeddings", "col_vector_2": "response_embeddings"})
            }
        ],
        source=JsonReader(fpath="{experiment_path}/interim_data/a.jsonl"),
        sink=JsonWriter(fpath="{experiment_path}/interim_data/b.jsonl"),
        plot=PlotlyChart(kind="table", title="Similarity score between question and response"),
    ))

    checks.append(SimpleCheck(
        name="distribution_of_extracted_text_embeddings",
        compute=[
            {
                "output_cols": ['extracted_text_embeddings_cosine_distribution'],
                "operator": Distribution(schema_data={"col_embs": "response_embeddings", "col_groupby": ["question_idx", "experiment_id"]}, kind="cosine_similarity"),
            }
        ],
        source=JsonReader(fpath="{experiment_path}/interim_data/embeddings.jsonl"),
        plot=PlotlyChart(kind="histogram", title="Cosine Similarity between extracted text embeddings", props=dict(x="extracted_text_embeddings_cosine_distribution", nbins=20, color='experiment_id')),
    ))

    checks.append(SimpleCheck(
        name="empty_response",
        compute=[
            {
                "output_cols": ["is_empty_response"],
                "operator": TextComparison(schema_data={"col_text": "response"}, reference_text='<EMPTY MESSAGE>')
            }
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
                "values": ["response_document_overlap_score", "similarity_score_between_question_and_extracted_text", "is_empty_response"],
                "columns": ["model"],
                "aggfunc": "mean"                
            },
        ]
        ),
    ))

    checks.append(SimpleCheck(
        name="question_umap",
        compute=[
            {
                "output_cols": [],
                "operator": UMAP(schema_data={"col_embs": "question_embeddings", "col_embs2": "response_embeddings"})
            }
        ],
        source=JsonReader(fpath="{experiment_path}/interim_data/embeddings.jsonl"),
        plot=PlotlyChart(kind="scatter", title="UMAP for question embeddings", props=dict(x='umap_0', y='umap_1', symbol='symbol', color='cluster')),
    ))


    checks.append(SimpleCheck(
        name="openai_grade",
        compute=[
            {
                "output_cols": ['chatgpt_model_grade_score'],
                "operator": ModelGradeScore(schema_data={"col_input": "prompt", "col_completion": "response"})
            }
        ],
        source=JsonReader(fpath="{experiment_path}/interim_data/c.jsonl"),
        plot=PlotlyChart(kind="table", title="ChatGPT graded score"),
    ))

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


openai.api_key = openai_api_key

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--start-streamlit", default=True, action="store_true")
    args = parser.parse_args()

    # start_streamlit()
    # import pdb; pdb.set_trace()

    user_inputs['evaluation_args'] = get_config()
    manager = ExperimentManager(user_inputs)
    manager.run()

    cfg = get_config()
    experiment_path = LOGS_DIR
    all_checks = copy.deepcopy(cfg['checks'])
    for check in all_checks:
        if check.source is not None:
            check.source.fpath = check.source.fpath.format(experiment_path=experiment_path)
        if check.sink is not None:
            check.sink.fpath = check.sink.fpath.format(experiment_path=experiment_path)
    cfg = Config(checks=all_checks, settings=Settings(logs_folder=LOGS_DIR, openai_api_key=openai_api_key))
    cfg.setup()
    for check in cfg.checks:
        results = check.make_executor(cfg.settings).run()

    if args.start_streamlit:
        start_streamlit()
