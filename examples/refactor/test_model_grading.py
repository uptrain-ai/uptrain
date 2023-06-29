import os
import polars as pl

from uptrain.framework import CheckSet, Settings, SimpleCheck
from uptrain.io import JsonReader, JsonWriter
from uptrain.operators import PlotlyChart, SelectOp
from uptrain.operators.language import ModelGradeScore, OpenAIGradeScore


def produce_dataset_w_context(source_path, sink_path):
    source = JsonReader(fpath=source_path)
    source.setup()
    data = source.run()["output"]

    assert data is not None
    # keep size small since we make a lot of openai calls
    data = data.with_columns(
        [pl.lit("gpt-4").alias("model"), pl.lit("context_retrieval").alias("pipeline")]
    ).sample(20)

    JsonWriter(fpath=sink_path).setup().run(data)


GRADING_PROMPT_TEMPLATE = """
{personality_description}

You are comparing a block quote to the document of information it was pulled from.
Here is the data:
[BEGIN DATA]
************
[Document]: {document}
************
[Submitted Quote]: {chunked_summary}
************
[END DATA]

Compare the factual content of the submitted quote with the document. Ignore any differences in style, grammar, or punctuation.
The submitted quote may either be a subset of the document, superset of the document, or it may conflict with it. Determine which case applies.
Answer the question by selecting one of the following options:

(A) The submitted quote is a subset of the document and is fully consistent with it.
(B) The submitted quote is a superset of the document, but is consistent with the document.
(C) The submitted quote is a superset of the document and is not consistent with the document.
"""


BOT_PERSONAS = {
    "analytical_validator": "You are an analytical and meticulous LLM with an emphasis on logical consistency and factual accuracy. Your purpose is to critically evaluate answers and ensure they align with the information presented in the document.",
    "contextual_inquirer": "You are a curious and context-oriented LLM, seeking to understand the underlying context and nuances of the document. You scrutinize answers to ensure they demonstrate a clear understanding of the document's context and maintain coherence with the presented information.",
    "evidential_fact-checker": "You are an evidence-driven LLM that places high importance on supporting facts and references. You diligently verify claims and check for evidence within the document to ensure answers rely on reliable information and align with the documented evidence.",
    "semantic_consistency_monitor": "You are a semantic-focused LLM with an eye for semantic coherence. Your role is to examine the semantic meaning and connections between the document and the answer, verifying that the answer accurately reflects the intended message and information conveyed in the document.",
    "contradiction_detector": "You are a contradiction-aware LLM, adept at identifying inconsistencies and contradictions. Your purpose is to meticulously analyze answers, cross-referencing statements with the document to identify any conflicting information and ensure consistency throughout.",
}


def partial_fmt(input_str, fill_param, fill_value):
    return input_str.replace("{" + fill_param + "}", fill_value)


def get_list_checks():
    column_to_ops = {}
    column_to_ops["chatgpt_model_grade"] = OpenAIGradeScore(
        col_in_input="document_text",
        col_in_completion="response",
        eval_name="coqa-closedqa-correct",
    )

    for persona, descr in BOT_PERSONAS.items():
        name = "custom_model_grade_" + persona
        column_to_ops[name] = ModelGradeScore(
            grading_prompt_template=partial_fmt(
                GRADING_PROMPT_TEMPLATE, "personality_description", descr
            ),
            eval_type="cot_classify",
            choice_strings=["A", "B", "C"],
            choice_scores={"A": 1.0, "B": 0.5, "C": 0.0},
            context_vars={
                "document": "document_text",
                "chunked_summary": "response",
            },
        )

    check = SimpleCheck(
        name="Model grade scores",
        sequence=[SelectOp(columns=column_to_ops)],
        plot=[PlotlyChart(kind="table", title="Model grade scores")],
    )

    return [check]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--start-streamlit", default=False, action="store_true")
    args = parser.parse_args()

    LOGS_DIR = "/tmp/uptrain_logs"
    original_dataset_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../datasets/qna_on_docs_samples.jsonl",
    )
    new_dataset_path = os.path.join("/tmp/_dataset_w_context.jsonl")
    produce_dataset_w_context(original_dataset_path, new_dataset_path)

    checkset = CheckSet(
        source=JsonReader(fpath=new_dataset_path),
        checks=get_list_checks(),
        settings=Settings(logs_folder=LOGS_DIR),
    )
    checkset.setup()
    checkset.run()

    if args.start_streamlit:
        from uptrain.dashboard import StreamlitRunner

        runner = StreamlitRunner(LOGS_DIR)
        runner.start()
