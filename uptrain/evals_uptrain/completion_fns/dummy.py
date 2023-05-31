import importlib
from typing import Optional
from evals.api import CompletionFn, CompletionResult

from evals.prompt.base import CompletionPrompt
from evals.record import record_sampling


class DummyCompletionResult(CompletionResult):
    def __init__(self, response) -> None:
        self.response = response

    def get_completions(self) -> list[str]:
        return [self.response.strip()]


class DummyCompletionFn(CompletionFn):
    def __init__(self, **kwargs) -> None:
        self.output_dictn = {}


    def __call__(self, prompt, **kwargs) -> DummyCompletionResult:
        prompt = CompletionPrompt(prompt).to_formatted_prompt()
        response = self.output_dictn[prompt]
        record_sampling(prompt=prompt, sampled=response)
        return DummyCompletionResult(response)
