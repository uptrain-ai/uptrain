from pydantic import BaseModel
import copy
from functools import partial
import pyarrow as pa
from uptrain.operators.language import GrammarScore, ModelGradingScore
import polars as pl
import numpy as np

from uptrain.operators.language.openai_evals import PromptEval, OpenaiEval
from uptrain.framework.config import Config, Settings, SimpleCheck
from uptrain.io import JsonReader, JsonWriter
from uptrain.operators.language.sql import GetSchemaDefinition


# -----------------------------------------------------------
# LLM Experiments - Run the model using given prompt template
# -----------------------------------------------------------

class LLMExperiment(BaseModel):
    """LLM Experiment to run the given model and prompt template"""

    prompt_template: str
    model: str
    cfg: dict
    dataset: str
    results: str
    id: int

    def make_executor(self):
        return LLMExperimentExecutor(exp=self)


class LLMExperimentExecutor:
    """ Executor of LLM Experiments """

    exp: LLMExperiment
    prompt_variables: list
    cfg: Config

    def __init__(self, exp: LLMExperiment) -> None:
        self.exp = exp
        self.cfg = Config(self.exp.cfg['checks'], self.exp.cfg['settings'])
        self.prompt_variables = [x.split("}")[0] for x in self.exp.prompt_template.split("{")[1:]]

    def run(self) -> None:

        samples = JsonReader(fpath=self.exp.dataset).make_executor().run()['output']

        eval_op = PromptEval(
            prompt_template=self.exp.prompt_template,
            prompt_variables=self.prompt_variables,
            gt_variables=[],
            model_name=self.exp.model
        )

        results = eval_op.make_executor().run(samples)

        responses = [x['sampled'] for x in results['extra']['final_report_indexed'].get_column('output_data')]
        prompts = [x['prompt'][0]['content'] for x in results['extra']['final_report_indexed'].get_column('data')]

        samples = samples.with_columns(pl.Series(name='response', values=responses))
        samples = samples.with_columns(pl.Series(name='prompt', values=prompts))
        samples = samples.with_columns(pl.Series(name='experiment_id', values=[self.exp.id] * len(responses)))
        JsonWriter(fpath=self.exp.results).make_executor().run(samples)

        return results

    def run_eval(self) -> None:
        self.cfg.setup()
        for check in self.cfg.checks:
            results = check.make_executor(self.cfg.settings).run()


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
    eval_metrics = []
    args = None

    def __init__(self, args: dict) -> None:
        self.args = args
        offset = 0
        args['experiment_args'].update({"experiment_identifiers": [{"Template": x} for x in range(len(args['experiment_args']['prompt_templates']))]})
        all_prompt_templates, all_identifiers = self._resolve_prompt_templates(args['experiment_args'])
        all_models = args['experiment_args']['model_names']
        for model in all_models:
            for idx in range(len(all_prompt_templates)):

                dataset_args = args['dataset_args']
                reader = JsonReader(fpath=dataset_args['file_name'])
                input_dataset = reader.make_executor().run()['output']
                questions = input_dataset['question']
                unique_questions = np.unique(np.array(questions))
                question_idx_dictn = dict(zip(list(unique_questions), range(len(unique_questions))))
                input_dataset = input_dataset.with_columns(pl.Series(name='question_idx', values=[question_idx_dictn[x] for x in list(questions)]))
                dataset_len = len(input_dataset)


                prompt_template = all_prompt_templates[idx]
                
                input_dataset = input_dataset.with_columns(pl.Series(name='row_idx', values=range(dataset_len)))
                input_dataset = input_dataset.with_columns(pl.Series(name='model', values=[model] * dataset_len))
                input_idxs = range(offset, offset+dataset_len)
                input_dataset = input_dataset.with_columns(pl.Series(name='idx', values=input_idxs))
                for key in all_identifiers[idx]:
                    input_dataset = input_dataset.with_columns(pl.Series(name=key, values=[all_identifiers[idx][key]] * dataset_len))
                experiment_path = args['evaluation_args']['log_folder'] + "/experiment_" + str(offset)

                # JsonWriter(fpath=experiment_path + "/input.jsonl").make_executor().run(input_dataset)
                JsonWriter(fpath=experiment_path + "/input_without_schema.jsonl").make_executor().run(input_dataset)

                # TODO figure out a better way to do this.
                with_schema_dataset_check = SimpleCheck(
                    name="get_schema_check",
                    compute=[
                        GetSchemaDefinition(),
                    ],
                    source=JsonReader(fpath=experiment_path + "/input_without_schema.jsonl"),
                    sink=JsonWriter(fpath=experiment_path + "/input.jsonl"),
                )
                with_schema_dataset_check.make_executor(Settings(logs_folder=experiment_path)).run()
                
                all_checks = copy.deepcopy(args['evaluation_args']['checks'])
                for check in all_checks:
                    if check.source is not None:
                        check.source.fpath = check.source.fpath.format(experiment_path=experiment_path)
                    if check.sink is not None:
                        check.sink.fpath = check.sink.fpath.format(experiment_path=experiment_path)
                experiment_cfg = {'checks': all_checks, 'settings': Settings(logs_folder=experiment_path)}

                self.experiments.append(LLMExperiment(
                    prompt_template=prompt_template,
                    model=model,
                    cfg=experiment_cfg,
                    dataset=experiment_path + "/input.jsonl",
                    results=experiment_path + "/output.jsonl",
                    id=idx
                ))
                offset += 1

    def _partial_format(self, txt, var, val):
        return txt.replace("{" + var + "}", val)


    def _resolve_prompt_templates(self, args: dict) -> None:
        all_prompt_templates = []
        all_identifiers = []
        for idx in range(len(args['prompt_templates'])):
            prompt_template = args['prompt_templates'][idx]
            experiment_identifier = args['experiment_identifiers'][idx]

            comparison_arg = args['comparison_args'][0]
            all_prompt_templates.extend([
                    self._partial_format(prompt_template, comparison_arg['comparison_variables'], x)
                for x in comparison_arg['comparison_options']
            ])
            for x in comparison_arg['comparison_options']:
                temp = copy.deepcopy(experiment_identifier)
                temp.update({comparison_arg['comparison_variables']: x})
                all_identifiers.append(temp)
        new_args = copy.deepcopy(args)
        new_args['prompt_templates'] = all_prompt_templates
        new_args['experiment_identifiers'] = all_identifiers
        new_args['comparison_args'] = args['comparison_args'][1:]
        if len(new_args['comparison_args']):
            return self._resolve_prompt_templates(new_args)
        else:
            return all_prompt_templates, all_identifiers

    def run(self):
        final_res = []

        for exp in self.experiments:
            exp_executor = exp.make_executor()
            results = exp_executor.run()

            samples = JsonReader(fpath=exp.results).make_executor().run()['output']
            final_res.append(samples)
        
        final_samples = pl.concat(final_res)
        JsonWriter(fpath=self.args['evaluation_args']['log_folder'] + "/output.jsonl").make_executor().run(final_samples)

            # if 'openai_model_grading' in self.eval_metrics:
            #     grading_op1 = OpenaiEval(
            #         bundle_path="",
            #         completion_name="gpt-3.5-turbo",
            #         eval_name="coqa-closedqa-correct",
            #     )
            #     al1 = grading_op1.make_executor().run(results)
            #     grading_op2 = OpenaiEval(
            #         bundle_path="",
            #         completion_name="gpt-3.5-turbo",
            #         eval_name="coqa-closedqa-conciseness",
            #     )
            #     al2 = grading_op2.make_executor().run(results)
            #     import pdb; pdb.set_trace()

            # score_op = GrammarScore(schema_data={"col_text": "sampled"})
            # grammar_results = score_op.make_executor().run(results)

            # import pdb; pdb.set_trace()
            # score_op1 = ModelGradingScore(schema_data={"col_prompt": "prompt", "col_answer": "sampled", "col_ideal": "sampled"})
            # model_grading_results = score_op1.make_executor().run(results)
            # final_res.update({
            #     exp.prompt_template: {
            #         'model_outputs': results.to_dict(),
            #         'grammar': grammar_results.to_dict()
            #     }
            # })
            # import pdb; pdb.set_trace()

        return results