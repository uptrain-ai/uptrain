"""
Implement checks to test language quality. 
"""

from __future__ import annotations
import asyncio
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
    wait as wait_for_futures,
)
import sys
import typing as t

try:
    import openai
except ImportError:
    openai = None
import aiolimiter
from loguru import logger
import tqdm
from tqdm.asyncio import tqdm_asyncio
from pydantic import BaseModel, Field

from uptrain.operators.base import *
from uptrain.utilities import dependency_required
if t.TYPE_CHECKING:
    from uptrain.framework.config import Settings


# -----------------------------------------------------------
# Make concurrent requests to the OpenAI or another LLM API
#
# Credits: https://github.com/cozodb/openai-multi-client/
# Seems to get stuck for me though.
# And zenoml code - https://github.com/zeno-ml/zeno-build/blob/main/zeno_build/models/providers/openai_utils.py
# -----------------------------------------------------------


class Payload(BaseModel):
    endpoint: str
    data: dict
    metadata: dict = Field(default_factory=dict)
    response: t.Any = None
    error: t.Optional[str] = None


def sync_process_payload(payload: Payload, max_retries: int) -> Payload:
    """TODO: add other endpoints here."""
    for _ in range(max_retries):
        try:
            if payload.endpoint == "chat.completions":
                payload.response = openai.ChatCompletion.create(**payload.data)
                break
            else:
                raise ValueError(f"Unknown endpoint: {payload.endpoint}")
        except Exception as exc:
            payload.error = str(exc)
            logger.error(f"Error when sending request to openai API: {payload.error}")
            if not isinstance(
                exc,
                (
                    openai.error.ServiceUnavailableError,
                    openai.error.APIError,
                    openai.error.RateLimitError,
                    openai.error.APIConnectionError,
                    openai.error.Timeout,
                ),
            ):
                break

    return payload


async def async_process_payload(
    payload: Payload, limiter: aiolimiter.AsyncLimiter, max_retries: int
) -> Payload:
    async with limiter:
        for _ in range(max_retries):  # failed requests don't count towards rate limit
            try:
                if payload.endpoint == "chat.completions":
                    payload.response = await openai.ChatCompletion.acreate(
                        **payload.data
                    )
                    break
                else:
                    raise ValueError(f"Unknown endpoint: {payload.endpoint}")
            except Exception as exc:
                payload.error = str(exc)
                logger.error(
                    f"Error when sending request to openai API: {payload.error}"
                )
                if isinstance(exc, openai.error.RateLimitError):
                    await asyncio.sleep(5)
                elif isinstance(
                    exc,
                    (
                        openai.error.ServiceUnavailableError,
                        openai.error.APIError,
                        openai.error.APIConnectionError,
                        openai.error.Timeout,
                    ),
                ):
                    continue
                else:
                    break

        return payload


@dependency_required(openai, "openai")
class LLMMulticlient:
    """
    Use multiple threads to send requests to the OpenAI API concurrently.
    """

    def __init__(self, settings: t.Optional[Settings] = None):
        self._max_retries = 2
        self._concurrency = 5

        if settings is not None:
            api_key = settings.check_and_get("openai_api_key")
            openai.api_key = api_key

    def fetch_responses(self, input_payloads: list[Payload]) -> list[Payload]:
        # return self.sync_fetch_responses(input_payloads)
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            logger.warning(
                "Detected Jupyter environment. Using multithreading to make concurrent api calls instead of asyncio."
            )
            return self.sync_fetch_responses(input_payloads)
        else:
            return asyncio.run(self.async_fetch_responses(input_payloads))

    def sync_fetch_responses(self, input_payloads: list[Payload]) -> list[Payload]:
        completed_futures = []
        num_active_requests = 0
        with ThreadPoolExecutor(max_workers=self._concurrency) as executor:
            futures = set()
            for data in tqdm.tqdm(input_payloads, desc="Request submitted to LLM"):
                if not num_active_requests < self._concurrency:
                    completed, futures = wait_for_futures(
                        futures, return_when="FIRST_COMPLETED"
                    )
                    completed_futures.extend(completed)

                futures.add(
                    executor.submit(sync_process_payload, data, self._max_retries)
                )
                num_active_requests += 1

            for future in as_completed(futures):
                completed_futures.append(future)

            output_payloads = []
            for future in completed_futures:
                try:
                    res = future.result()
                except Exception as exc:
                    logger.error(f"Error when sending request to openai API: {exc}")
                    res = None
                output_payloads.append(res)
                num_active_requests -= 1

        return output_payloads

    async def async_fetch_responses(
        self, input_payloads: list[Payload]
    ) -> list[Payload]:
        # TODO: make rate limiting customizable
        limiter = aiolimiter.AsyncLimiter(20, time_period=5)
        async_outputs = [
            async_process_payload(data, limiter, self._max_retries)
            for data in input_payloads
        ]
        output_payloads = await tqdm_asyncio.gather(*async_outputs)
        return output_payloads
