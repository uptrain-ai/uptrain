"""
Implement checks to test language quality. 
"""

from __future__ import annotations
import threading
import time
import typing as t
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
    wait as wait_for_futures,
)

try:
    import openai
except ImportError:
    openai = None
import tenacity
import tqdm
from pydantic import BaseModel, Field

from uptrain.framework.config import Settings
from uptrain.operators.base import *
from uptrain.utilities import dependency_required


# -----------------------------------------------------------
# Make concurrent requests to the OpenAI or another LLM API
#
# Credits: https://github.com/cozodb/openai-multi-client/
# It seems to get stuck for me.
# -----------------------------------------------------------


class Payload(BaseModel):
    endpoint: str
    data: dict
    metadata: dict = Field(default_factory=dict)
    response: t.Any = None
    error: t.Optional[str] = None
    should_retry: bool = False


def process_payload(payload: Payload) -> Payload:
    """TODO: add other endpoints here."""
    try:
        if payload.endpoint == "chat.completions":
            payload.response = openai.ChatCompletion.create(**payload.data)
        else:
            raise ValueError(f"Unknown endpoint: {payload.endpoint}")
    except Exception as exc:
        payload.error = str(exc)
        if isinstance(
            exc,
            (
                openai.error.ServiceUnavailableError,
                openai.error.APIError,
                openai.error.RateLimitError,
                openai.error.APIConnectionError,
                openai.error.Timeout,
            ),
        ):
            payload.should_retry = True

    return payload


@dependency_required(openai, "openai")
class LLMMulticlient:
    def __init__(
        self, concurrency=5, max_retries=2, settings: t.Optional[Settings] = None
    ):
        self._max_retries = max_retries
        self._concurrency = concurrency

        self._num_active_requests = 0
        self._lock = threading.Lock()

        if settings is not None:
            openai.api_key = settings.openai_api_key

    def worker_available(self):
        """TODO: Add request/min and tokens/min checks to this."""
        with self._lock:
            if self._num_active_requests < self._concurrency:
                return True
            else:
                return False

    def fetch_responses(self, input_payloads: list[Payload]) -> list[Payload]:
        fetch_method = tenacity.retry(
            wait=tenacity.wait_fixed(1),
            stop=tenacity.stop_after_attempt(self._max_retries),
            retry=tenacity.retry_if_result(lambda payload: payload.should_retry),
        )(process_payload)

        output_payloads = []
        with ThreadPoolExecutor(max_workers=self._concurrency) as executor:
            futures = set()
            for data in tqdm.tqdm(input_payloads, desc="Request submitted to LLM"):
                while not self.worker_available():
                    time.sleep(1)

                futures.add(executor.submit(fetch_method, data))
                self._num_active_requests += 1

                if not len(futures) < self._concurrency:
                    completed, futures = wait_for_futures(
                        futures, return_when="FIRST_COMPLETED"
                    )
                    for future in completed:
                        output_payloads.append(future.result())
                        self._num_active_requests -= 1

            for future in as_completed(futures):
                output_payloads.append(future.result())
                self._num_active_requests -= 1

        return output_payloads
