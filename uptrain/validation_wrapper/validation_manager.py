from pydantic import BaseModel
import typing as t
import polars as pl
from loguru import logger

from uptrain.framework.signal import Signal
from uptrain.framework.checks import Check, Settings


class ValidationManager(BaseModel):
    check: t.Any
    completion_function: t.Any
    retry_logic: list[dict]
    pass_condition: t.Any
    max_retries: int = 3

    def setup(self):
        self.check.setup(Settings())

    def run(self, inputs):
        for key in inputs.keys():
            inputs[key] = [inputs[key]]
        response_is_valid = False
        num_tries = 0
        completion_function = self.completion_function
        response_history = {}
        while not response_is_valid:
            response = completion_function(inputs)
            response_history.update({'attempt_' + str(num_tries): response})
            num_tries += 1
            inputs["response"] = [response]
            data = pl.from_dict(inputs)
            data = self.check.run(data)
            response_is_valid = self.pass_condition.run(data)[0]

            if response_is_valid:
                logger.success(f"Validation check PASSED after {num_tries} attempt(s)")                
            elif num_tries < self.max_retries:
                completion_function = self.completion_function
                selected_retry_function = "default"
                for retry_condition in list(self.retry_logic):
                    if retry_condition['signal'].run(data)[0] == True:
                        completion_function = retry_condition['completion_function']
                        selected_retry_function = retry_condition['name']
                        break
                logger.warning(f"RETRYING validation check {num_tries} of {self.max_retries} with logic: {selected_retry_function}")
            else:
                response_is_valid = True
                logger.warning(f"Validation check FAILED after {self.max_retries} attempt(s)")
        if num_tries > 1:
            logger.info(f"Response History: {response_history}")

        return response
