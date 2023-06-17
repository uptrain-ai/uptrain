import os
os.environ['OPENAI_API_KEY'] = "..."

from uptrain.framework import CheckSet, Settings, SimpleCheck
from uptrain.operators import (
    PlotlyChart,
)
from uptrain.io import JsonReader
from uptrain.operators.language import (
    OpenAIGradeScore,
    ModelGradeScore
)

source_path = "..."
LOGS_DIR = "uptrain_logs"


def resolve_prompts(template, resolver_args):
    prompt_variables = [x.split("}")[0] for x in template.split("{")[1:]]
    resolved_prompts = []
    for resolver_arg in resolver_args:
        resolved_prompt = template
        for prompt_var in prompt_variables:
            if prompt_var in resolver_arg:
                resolved_prompt = resolved_prompt.replace('{'+f'{prompt_var}'+'}', resolver_arg[prompt_var])
        resolved_prompts.append(resolved_prompt)
    return resolved_prompts


grading_prompt_template = """
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


bot_personalities = {
    'analytical_validator': 'You are an analytical and meticulous LLM with an emphasis on logical consistency and factual accuracy. Your purpose is to critically evaluate answers and ensure they align with the information presented in the document.',
    'contextual_inquirer': "You are a curious and context-oriented LLM, seeking to understand the underlying context and nuances of the document. You scrutinize answers to ensure they demonstrate a clear understanding of the document's context and maintain coherence with the presented information.",
    'evidential_fact-checker': "You are an evidence-driven LLM that places high importance on supporting facts and references. You diligently verify claims and check for evidence within the document to ensure answers rely on reliable information and align with the documented evidence.",
    'semantic_consistency_monitor': "You are a semantic-focused LLM with an eye for semantic coherence. Your role is to examine the semantic meaning and connections between the document and the answer, verifying that the answer accurately reflects the intended message and information conveyed in the document.",
    'contradiction_detector': "You are a contradiction-aware LLM, adept at identifying inconsistencies and contradictions. Your purpose is to meticulously analyze answers, cross-referencing statements with the document to identify any conflicting information and ensure consistency throughout."
}


def get_checkset():
    custom_grade_checks = [SimpleCheck(
        name="openai_grade",
        compute=[
            OpenAIGradeScore(
                col_in_input="document_text",
                col_in_completion="response",
                col_out="chatgpt_model_grade_score",
                eval_name="coqa-closedqa-correct"
            ),
        ],
        plot=PlotlyChart(kind="table", title="ChatGPT graded score"),
    )]

    grading_prompts = resolve_prompts(
        template=grading_prompt_template,
        resolver_args=[{"personality_description": x} for x in list(bot_personalities.values())]
    )

    for idx in range(len(grading_prompts)):
        custom_grade_checks.append(SimpleCheck(
            name="custom_model_grade_" + list(bot_personalities.keys())[idx],
            compute=[
                ModelGradeScore(
                    col_in_input="document_text",
                    col_in_completion="response",
                    col_out=list(bot_personalities.keys())[idx] + "_custom_model_grade_score",
                    grading_prompt_template=grading_prompts[idx],
                    eval_type="cot_classify",
                    choice_strings=[
                        "(A) The submitted quote is a subset of the document and is fully consistent with it.",
                        "(B) The submitted quote is a superset of the document, but is consistent with the document.",
                        "(C) The submitted quote is a superset of the document and is not consistent with the document."
                    ],
                    choice_scores={
                        "(A) The submitted quote is a subset of the document and is fully consistent with it.": 1.0,
                        "(B) The submitted quote is a superset of the document, but is consistent with the document.": 0.5,
                        "(C) The submitted quote is a superset of the document and is not consistent with the document.": 0.0
                    },
                    grading_prompt_mapping={
                        "document_text": "document",
                        "response": "chunked_summary"
                    }
                ),
            ],
            plot=PlotlyChart(kind="table", title="Custom Model graded score " + list(bot_personalities.keys())[idx],
            ),
        ))


    checkset = CheckSet(
        source=JsonReader(fpath=source_path),
        checks=custom_grade_checks,
        settings=Settings(logs_folder=LOGS_DIR),
    )

    return checkset

# -----------------------------------------------------------
# Starting a streamlit server to visualize the results
# -----------------------------------------------------------

def start_streamlit():
    from uptrain.dashboard import StreamlitRunner

    runner = StreamlitRunner(LOGS_DIR)
    runner.start()


if __name__ == "__main__":
    cfg = get_checkset()
    cfg.setup()
    cfg.run()

    start_streamlit()
    import pdb; pdb.set_trace()

