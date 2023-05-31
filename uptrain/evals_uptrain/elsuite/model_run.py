from typing import Any

import evals
import evals.metrics
from evals.api import CompletionFn
from evals.prompt.base import is_chat_prompt


class ModelRun(evals.Eval):
    def __init__(
        self,
        completion_fns: list[CompletionFn],
        samples_jsonl: str,
        *args,
        max_tokens: int = 500,
        **kwargs,
    ):
        super().__init__(completion_fns, *args, **kwargs)
        assert len(completion_fns) == 1, "Match only supports one completion fn"
        self.max_tokens = max_tokens
        self.samples_jsonl = samples_jsonl

    def eval_sample(self, sample: Any, *_):
        prompt = sample["input"]
        result = self.completion_fn(
            prompt=prompt,
            temperature=0.0,
        )
        sampled = result.get_completions()[0]

        return evals.record_and_check_match(
            prompt=prompt,
            sampled=sampled,
            expected="",
        )

    def run(self, recorder):
        samples = self.get_samples()
        self.eval_all_samples(recorder, samples)
        model_outputs = []
        for x in recorder._events:
            if 'prompt' in x.data:
                model_outputs.append(x.data)
        return model_outputs
