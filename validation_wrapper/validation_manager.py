from pydantic import BaseModel
import typing as t
import polars as pl

from uptrain.framework.signal import Signal
from uptrain.framework.checks import Check, Settings


class ValidationManager(BaseModel):
    check: t.Any
    completion_fn: t.Any
    pass_condition: t.Any
    max_retries: int = 3

    def setup(self):
        self.check.setup(Settings())

    def run(self, inputs):
        for key in inputs.keys():
            inputs[key] = [inputs[key]]
        response_is_valid = False
        num_tries = 0
        while not response_is_valid:
            response = self.completion_fn(inputs)
            inputs["response"] = [response]
            data = pl.from_dict(inputs)
            data = self.check.run(data)
            response_is_valid = self.pass_condition.run(data)[0]

            num_tries += 1
            if num_tries > self.max_retries:
                response_is_valid = True

        return response
