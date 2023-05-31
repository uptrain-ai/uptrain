from pydantic import BaseModel
import copy
from functools import partial
import pyarrow as pa
from uptrain.operators.language import GrammarScore, ModelGradingScore
import polars as pl

from uptrain.operators.language.openai_evals import PromptEval


# -----------------------------------------------------------
# LLM Experiments - Run the model using given prompt template
# -----------------------------------------------------------

class LLMExperiment(BaseModel):
    """LLM Experiment to run the given model and prompt template"""

    prompt_template: str
    model: str

    def make_executor(self):
        return LLMExperimentExecutor(exp=self)


class LLMExperimentExecutor:
    """ Executor of LLM Experiments """

    exp: LLMExperiment
    prompt_variables: list

    def __init__(self, exp: LLMExperiment) -> None:
        self.exp = exp
        self.prompt_variables = [x.split("}")[0] for x in self.exp.prompt_template.split("{")[1:]]

    def run(self, samples) -> None:

        eval_op = PromptEval(
            prompt_template=self.exp.prompt_template,
            prompt_variables=self.prompt_variables,
            gt_variables=[],
            model_name=self.exp.model
        )

        results = eval_op.make_executor().run(samples)
        return results


# {
#     "prompt_templates": ["Imagine you are a {persona} who will explain the given concept in 10 words only. Explain {concept}: "],
#     "model_names": ["gpt-3.5-turbo", 'claude'],
#     "comparison_args": [{
#         "comparison_variables": 'persona',
#         'comparison_options': ['school teacher', 'subject matter expert', 'youtube celebrity', 'scientist', 'college professor']
#     }],
# },


class ExperimentManager:

    experiments = []

    def __init__(self, args: dict) -> None:
        self.personas = args['comparison_args'][0]['comparison_options']
        all_prompt_templates = self._resolve_prompt_templates(args)
        all_models = args['model_names']
        for model in all_models:
            for prompt_template in all_prompt_templates:
                self.experiments.append(LLMExperiment(
                    prompt_template=prompt_template,
                    model=model
                ))

    def _partial_format(self, txt, var, val):
        return txt.replace("{" + var + "}", val)


    def _resolve_prompt_templates(self, args: dict) -> None:
        all_prompt_templates = []
        for prompt_template in args['prompt_templates']:
            comparison_arg = args['comparison_args'][0]
            all_prompt_templates.extend([
                    self._partial_format(prompt_template, comparison_arg['comparison_variables'], x)
                for x in comparison_arg['comparison_options']
            ])
        new_args = copy.deepcopy(args)
        new_args['prompt_templates'] = all_prompt_templates
        new_args['comparison_args'] = args['comparison_args'][1:]
        if len(new_args['comparison_args']):
            return self._resolve_prompt_templates(new_args)
        else:
            return all_prompt_templates

    def run(self, samples):
        final_results = pl.DataFrame()
        for exp in self.experiments:
            results = exp.make_executor().run(samples)
            results = pl.from_dict({
                'prompt': [str(x['prompt'][0]) for x in results['extra']['final_report']],
                'output': [x['sampled'][0] for x in results['extra']['final_report']]
            })

            # Add concept and feature to the results
            for attr in samples.columns:
                results = results.with_columns(pl.lit(samples.get_column(attr)))

            # Add model to the results
            results = results.with_columns(pl.lit(exp.model).alias("model"))
    
            # GRAMMAR SCORE
            score_op = GrammarScore(schema_data={"col_text": "output"})
            grammar_results = score_op.make_executor().run(results)
            # Add gramar scores to the results
            results = results.with_columns(pl.lit("grammar").alias("metric"), pl.lit(list(grammar_results.values())[0]).alias("score"))
        
            # MODEL GRADING SCORE
            score_op1 = ModelGradingScore(schema_data={"col_prompt": "prompt", "col_answer": "output", "col_ideal": "output"})
            model_grading_results = score_op1.make_executor().run(results)
            # Add model grading scores to the results
            results = results.extend(results.with_columns(pl.lit("model_grading").alias("metric"), pl.lit(list(model_grading_results.values())[0]).alias("score")))

            # Remove prompt columns
            results = results.drop("prompt")

            # Add results to final_results
            if final_results.is_empty():
                final_results = results
            else:
                final_results.extend(results)            

        # Add personas to final_results
        final_results = final_results.with_row_count().with_columns(
            (pl.col("row_nr") // int((len(final_results) / len(self.personas))))
            .apply(lambda idx: self.personas[idx])
            .alias("persona")
        )

        return final_results
