"""This module implements an `Experiment` object used to evaluate 
how different prompts/LLM-input-parameters affect the model performance.
"""

from __future__ import annotations
import itertools
import os
import typing as t

import polars as pl

from uptrain.operators.base import *
from uptrain.utilities import jsonload, jsondump, to_py_types, clear_directory
from uptrain.framework.base import OperatorDAG, Settings
from uptrain.framework.checks import *


class PromptExperiment:
    """An experiment that runs a prompt on a set of models and checks the results.

    Attributes:
        prompt_template: A string template for the prompt.
        prompt_params: A dictionary mapping parameter names to lists of values.
            The cartesian product of all the parameter values will be used to
            construct the prompts.
        models: A list of models to run the experiment on.
        source: The source of the data to run the experiment on.
        checks: A list of checks to run on the completion data.
    """

    prompt_template: str
    prompt_params: dict[str, list[str]]
    models: list[str]
    source: str
    checks: list[SimpleCheck]
    settings: "Settings"

    def __init__(
        self,
        prompt_template: str,
        prompt_params: dict[str, list[str]],
        models: list[str],
        source: str,
        checks: list[SimpleCheck],
        settings: "Settings",
    ):
        self.prompt_template = prompt_template
        self.prompt_params = prompt_params
        self.models = models
        self.source = source
        self.checks = checks
        self.settings = settings

    def setup(self, settings: "Settings" | None = None):
        return self

    def run(self):
        """Runs the experiment.

        - Construct all the prompt variations and generate completions for each.
        - Run the checks on the completion data.
        """
        # construct prompts by formatting the prompt template with all combinations of prompt params
        input_data = []
        for combos in itertools.product(
            list(self.prompt_params.values()) + [self.models]
        ):
            prompt_params, model = combos[:-1], combos[-1]
            variables = dict(zip(self.prompt_params.keys(), prompt_params))
            prompt = self.prompt_template.format(**variables)
            input_data.append(
                {
                    "template": self.prompt_template,
                    "prompt": prompt,
                    **variables,
                    "model": model,
                }
            )
        input_dataset = pl.DataFrame(input_data)

        # Use the PromptEval operator to generate completions for each prompt
