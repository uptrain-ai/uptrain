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
        final_res = {}
        for exp in self.experiments:
            results = exp.make_executor().run(samples)
            results = pl.from_dict({
                'prompt': [x['prompt'] for x in results['extra']['final_report']],
                'sampled': [x['sampled'][0] for x in results['extra']['final_report']]
            })
            score_op = GrammarScore(schema_data={"col_text": "sampled"})
            grammar_results = score_op.make_executor().run(results)

            import pdb; pdb.set_trace()
            score_op1 = ModelGradingScore(schema_data={"col_prompt": "prompt", "col_answer": "sampled", "col_ideal": "sampled"})
            model_grading_results = score_op1.make_executor().run(results)
            final_res.update({
                exp.prompt_template: {
                    'model_outputs': results.to_dict(),
                    'grammar': grammar_results.to_dict()
                }
            })
            import pdb; pdb.set_trace()

        return results