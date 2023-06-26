from sql_config import *
from manager import ExperimentManager, ExperimentArgs, EvalArgs, PromptResolver
from uptrain.io import JsonReader
from uptrain.framework.base import Settings

from uptrain.operators.language import (
    ModelGradeScore
)

input_dataset = '/Users/sourabhagrawal/Desktop/codes/llm/uptrain_experiments/uptrain/examples/refactor/SQL_small_input.jsonl'
input_dataset = '/Users/bhanu/src/uptrain_experiments/llm/sql_new_small_input.jsonl'
experiment_manager = ExperimentManager(
    prompt_template=prompt_template,
    model="gpt-3.5-turbo",
    checks=[
        select_all_check,
        sql_validity_check,
        # schema_validity_check,
        execution_accuracy_check
    ],
    prompt_resolver_dictn={'persona': 'bot'},
    dataset=JsonReader(fpath=input_dataset),
    dataset_variables=['question', 'schema_def', 'dialect']
)


executor = experiment_manager.make_executor(settings=Settings(logs_folder="sql_uptrain_logs"))

# # # Run base experiment
executor.run_base()

# # Run for different personas
executor.run_experiments(ExperimentArgs(prompt_resolvers=[{'persona': 'bot'}, {'persona': 'Data Engineer'}]))
import pdb; pdb.set_trace()

# # # Run for different models
# executor.run_experiments(ExperimentArgs(models=['cohere', 'gpt-3.5-turbo']))
import pdb; pdb.set_trace()

# # Run for a new eval
executor.run_new_evals(EvalArgs(checks=[empty_response_check]))

# Add new eval for future experiments
executor.add_new_evals([empty_response_check])

# Run for different personas + personality traits
executor.run_experiments(ExperimentArgs(
    prompt_template=personality_prompt_template,
    prompt_resolvers=[
        {'persona': 'analytical_validator', 'personality': 'You are an analytical and meticulous LLM with an emphasis on logical consistency and factual accuracy. Your purpose is to critically evaluate answers and ensure they align with the information presented in the document.'}, 
        {'persona': 'contextual_inquirer', 'personality': "You are a curious and context-oriented LLM, seeking to understand the underlying context and nuances of the document. You scrutinize answers to ensure they demonstrate a clear understanding of the document's context and maintain coherence with the presented information."},
        {'persona': 'evidential_fact-checker', 'personality': 'You are an evidence-driven LLM that places high importance on supporting facts and references. You diligently verify claims and check for evidence within the document to ensure answers rely on reliable information and align with the documented evidence.'},
        {'persona': 'semantic_consistency_monitor', 'personality': 'You are a semantic-focused LLM with an eye for semantic coherence. Your role is to examine the semantic meaning and connections between the document and the answer, verifying that the answer accurately reflects the intended message and information conveyed in the document.'},
    ]
))


# Either run across multiple models
# Or Run across multiple prompts
-  Prompt 



bot_personalities = {
    'analytical_validator': 'You are an analytical and meticulous LLM with an emphasis on logical consistency and factual accuracy. Your purpose is to critically evaluate answers and ensure they align with the information presented in the document.',
    'contextual_inquirer': "You are a curious and context-oriented LLM, seeking to understand the underlying context and nuances of the document. You scrutinize answers to ensure they demonstrate a clear understanding of the document's context and maintain coherence with the presented information.",
    'evidential_fact-checker': "You are an evidence-driven LLM that places high importance on supporting facts and references. You diligently verify claims and check for evidence within the document to ensure answers rely on reliable information and align with the documented evidence.",
    'semantic_consistency_monitor': "You are a semantic-focused LLM with an eye for semantic coherence. Your role is to examine the semantic meaning and connections between the document and the answer, verifying that the answer accurately reflects the intended message and information conveyed in the document.",
    'contradiction_detector': "You are a contradiction-aware LLM, adept at identifying inconsistencies and contradictions. Your purpose is to meticulously analyze answers, cross-referencing statements with the document to identify any conflicting information and ensure consistency throughout."
}

grading_prompts = PromptResolver(
    template=grading_prompt_template,
    resolver_args=[{"personality_description": x} for x in list(bot_personalities.values())]
).make_executor().run()

custom_grade_checks = []
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
executor.run_new_evals(EvalArgs(checks=custom_grade_checks))


