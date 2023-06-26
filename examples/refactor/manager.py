import copy
from uptrain.framework.base import OperatorDAG, Settings
from uptrain.framework.checks import SimpleCheck, CheckSet
from uptrain.operators import ColumnExpand, Concatenation, PlotlyChart
from uptrain.operators.language import PromptEval
from uptrain.io import DeltaWriter, JsonReader, JsonWriter, DeltaReader
from uptrain.dashboard import StreamlitRunner

import polars as pl
import numpy as np
import os
import shutil
from pydantic import BaseModel
import typing as t
from functools import reduce
from operator import concat


class PromptResolver(BaseModel):
    template: str
    resolver_args: list[dict]

    def make_executor(self, settings: t.Optional[Settings] = None):
        return PromptResolverExecutor(self)


class PromptResolverExecutor:
    op: PromptResolver

    def __init__(self, op: PromptResolver) -> None:
        self.op = op

    def _extract_prompt_variables(self, prompt) -> list[str]:
        return [x.split("}")[0] for x in prompt.split("{")[1:]]

    def run(self) -> list[str]:
        prompt_variables = self._extract_prompt_variables(self.op.template)
        resolved_prompts = []
        for resolver_arg in self.op.resolver_args:
            resolved_prompt = self.op.template
            for prompt_var in prompt_variables:
                if prompt_var in resolver_arg:
                    resolved_prompt = resolved_prompt.replace('{'+f'{prompt_var}'+'}', resolver_arg[prompt_var])
            resolved_prompts.append(resolved_prompt)
        return resolved_prompts



class Experiment(BaseModel):
    id: t.Union[int, str]
    prompt: str
    model: str
    dictn: dict

    def __str__(self) -> str:
        return str(self.id)


class ExperimentArgs(BaseModel):
    prompt_template: t.Optional[str] = None
    models: t.Optional[list[str]] = None
    prompt_resolvers: t.Optional[list[dict]] = None


class EvalArgs(BaseModel):
    checks: list


class ExperimentManager(BaseModel):
    prompt_template: str
    model: str
    checks: list
    prompt_resolver_dictn: dict
    dataset: t.Any
    dataset_variables: list[str]

    def make_executor(self, settings: t.Optional[Settings] = None):
        return ExperimentManagerExecutor(self, settings)


class ExperimentManagerExecutor:
    op: ExperimentManager
    _experiment_id: int = -1

    def __init__(self, op: ExperimentManager, settings: t.Optional[Settings] = None):
        self.op = op
        self.settings = settings
        if os.path.exists(settings.logs_folder):
            shutil.rmtree(settings.logs_folder)


    def __str__(self) -> str:
        return "experiment_manager"

    def assign_experiment_id(self):
        self._experiment_id += 1
        return self._experiment_id

    def _extract_prompt_variables(self, prompt) -> list[str]:
        return [x.split("}")[0] for x in prompt.split("{")[1:]]

    def _combine_plot_operators(self, plots=[]):
        # assert(list(np.unique(np.array([x.kind for x in plots]))) == ["table"], "all the plots should be table")
        return PlotlyChart(
            kind='table',
            title='Experiment Summary Table'
            # title='_and_'.join([x.title for x in plots]),
            # filter_on=reduce(concat, [x.filter_on for x in plots]),
            # pivot_args=reduce(concat, [x.pivot_args for x in plots]),
        )


    def _run_experiments(self, experiments, checks):
        # TODO: Instead of below, create a single optimised DAG and execute it
        model_outputs = []
        for experiment in experiments:

            print(f"Starting to execute Experiment: {experiment}")

            # TODO: What should be the logic for 
            input = self.op.dataset.make_executor().run()['output']
            dataset_creation_check = SimpleCheck(
                name=str(experiment) + "_dataset_creation",
                compute=[ColumnExpand(col_out_names=list(experiment.dictn.keys()), col_vals=list(experiment.dictn.values()))],
            )
            output = dataset_creation_check.make_executor(self.settings).run(input)
            sink = DeltaWriter(fpath=os.path.join(self.settings.logs_folder, str(experiment), "dataset"))
            sink.make_executor().run(output)


            input = sink.to_reader().make_executor().run()['output']
            model_run_check = SimpleCheck(
                name=str(experiment) + "_model_run",
                compute=[PromptEval(
                    prompt_template=experiment.prompt,
                    prompt_variables=self.op.dataset_variables,
                    gt_variables=[],
                    model_name=experiment.model
                )],
                # source=dataset_creation_check.sink.to_reader(),
                # sink=DeltaWriter(fpath=os.path.join(self.settings.logs_folder, str(experiment), "model_output")),
            )
            output = model_run_check.make_executor(self.settings).run(input)
            sink = DeltaWriter(fpath=os.path.join(self.settings.logs_folder, str(experiment), "model_output"))
            sink.make_executor().run(output)

            print(f"Finished Experiment: {experiment}")

            model_outputs.append(sink.to_reader())

        # TODO: We should first run all the checks and then aggregate
        # Need to change the ploting function for the same

        concat_check = SimpleCheck(
            name="model_run_concatenation",
            compute=[Concatenation(readers=model_outputs)],
            # sink=DeltaWriter(fpath=os.path.join(self.settings.logs_folder,  "model_output")),
        )
        output = concat_check.make_executor(self.settings).run()
        sink = DeltaWriter(fpath=os.path.join(self.settings.logs_folder, "agg_" + ",".join([str(x) for x in experiments]), "model_output"))
        sink.make_executor(Settings(logs_folder=os.path.join(self.settings.logs_folder, "agg_" + ",".join([str(x) for x in experiments])))).run(output)

        cfg_checks = []
        # cfg_checks.append(concat_check)
        operators = []
        plots = []
        names = []
        for check in checks:
            # if check.source is None:
            if check.plot is not None:
                # if check.plot.kind == 'table':
                operators.extend(check.compute)
                # plots.append(check.plot)
                names.append(check.name)
            cfg_checks.append(check)

        if len(operators) or len(plots):
            new_check = SimpleCheck(
                name='Experiment Summary',
                compute=operators,
                # source=concat_check.sink.to_reader(),
                plot=self._combine_plot_operators()                
            )
            cfg_checks.append(new_check)

        checkset = CheckSet(
            source=sink.to_reader(),
            checks=cfg_checks,
            settings=Settings(logs_folder=os.path.join(self.settings.logs_folder, "agg__" + ",".join([str(x) for x in experiments]))),
        )
        checkset.setup()
        checkset.run()


        # cfg = Config(
        #     checks=cfg_checks,
        #     settings=Settings(logs_folder=os.path.join(self.settings.logs_folder, "agg_" + ",".join([str(x) for x in experiments]))),
        # )
        # cfg.setup()
        # for check in cfg_checks:
        #     if check.name == "model_run_concatenation":
        #         check.make_executor(cfg.settings).run(pl.DataFrame())
        #     else:
        #         check.make_executor(cfg.settings).run()

        runner = StreamlitRunner(checkset.settings.logs_folder)
        runner.start()
        import pdb; pdb.set_trace()


    def run_experiments(self, experiment_args: ExperimentArgs) -> None:
        prompt_template = experiment_args.prompt_template
        if prompt_template is None:
            prompt_template = self.op.prompt_template

        num_experiments = max(
            0 if experiment_args.prompt_resolvers is None else len(experiment_args.prompt_resolvers),
            0 if experiment_args.models is None else len(experiment_args.models)
        )

        assert(num_experiments > 0, "Need atleast one experiment to run")

        if experiment_args.prompt_resolvers is None:
            prompt_resolver_args = [copy.deepcopy(self.op.prompt_resolver_dictn)] * num_experiments
        else:
            prompt_resolver_args = [{**copy.deepcopy(self.op.prompt_resolver_dictn), **x} for x in experiment_args.prompt_resolvers]
        resolved_prompts = PromptResolver(template=prompt_template, resolver_args=prompt_resolver_args).make_executor().run()

        if experiment_args.models is None:
            resolved_models = [self.op.model] * num_experiments
        else:
            resolved_models = experiment_args.models

        experiments = []
        for idx in range(len(resolved_prompts)):
            experiment_dictn = {**{'prompt_template': prompt_template, 'model': resolved_models[idx]}, **prompt_resolver_args[idx]}
            experiments.append(Experiment(
                id=self.assign_experiment_id(),
                prompt=resolved_prompts[idx],
                model=resolved_models[idx],
                dictn=experiment_dictn
            ))
        self._run_experiments(experiments, self.op.checks)


    def run_base(self, checks: list[SimpleCheck] = None) -> None:
        if checks is None:
            checks = self.op.checks
        resolved_prompt = PromptResolver(template=self.op.prompt_template, resolver_args=[self.op.prompt_resolver_dictn]).make_executor().run()[0]
        experiments = [Experiment(
            id=self.assign_experiment_id(),
            prompt=resolved_prompt,
            model=self.op.model,
            dictn={**{'prompt_template': self.op.prompt_template, 'model': self.op.model}, **self.op.prompt_resolver_dictn}
        )]
        self._run_experiments(experiments, checks)


    def run_new_evals(self, eval_args: EvalArgs) -> None:
        assert(len(eval_args.checks) > 0, "Need atleast one check to run")
        self.run_base(eval_args.checks)


    def add_new_evals(self, new_evals) -> None:
        self.op.checks.extend(new_evals)
        # Save new state to database


    def modify_dataset(self, new_dataset) -> None:
        self.op.dataset = new_dataset
        # Save new state to database


    def modify_base_prompt(self, new_prompt) -> None:
        self.op.prompt_template = new_prompt
        # Save new state to database


    def modify_base_model(self, new_model) -> None:
        self.op.model = new_model
        # Save new state to database


    def modify_base_prompt_resolvers(self, new_prompt_resolvers) -> None:
        self.op.prompt_resolver_dictn.update(new_prompt_resolvers)
        # Save new state to database
