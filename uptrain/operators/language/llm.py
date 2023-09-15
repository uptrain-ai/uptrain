"""
Implement checks to test language quality. 
"""

from __future__ import annotations
import asyncio
from concurrent.futures import ThreadPoolExecutor
import random
import typing as t

import aiolimiter
from loguru import logger
from tqdm.asyncio import tqdm_asyncio
from pydantic import BaseModel, Field

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.utilities import lazy_load_dep

openai = lazy_load_dep("openai", "openai")
if t.TYPE_CHECKING:
    import openai
    import openai.error


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


async def async_process_payload(
    payload: Payload, limiter: aiolimiter.AsyncLimiter, max_retries: int
) -> Payload:
    async with limiter:
        for count in range(
            max_retries
        ):  # failed requests don't count towards rate limit
            try:
                if payload.endpoint == "chat.completions":
                    payload.response = await openai.ChatCompletion.acreate(
                        **payload.data, request_timeout=10
                    )
                    break
                else:
                    raise ValueError(f"Unknown endpoint: {payload.endpoint}")
            except Exception as exc:
                logger.error(
                    f"Error when sending request to openai API: {payload.error}"
                )
                if (
                    isinstance(
                        exc,
                        (
                            openai.error.ServiceUnavailableError,
                            openai.error.APIConnectionError,
                            openai.error.RateLimitError,
                            openai.error.APIError,
                            openai.error.Timeout,
                            openai.error.TryAgain,
                        ),
                    )
                    and count < max_retries - 1
                ):
                    await asyncio.sleep(random.uniform(0.5, 1.5) * count + 1)
                elif (
                    isinstance(exc, openai.error.InvalidRequestError)
                    and "context_length" in exc.code
                    and count < max_retries - 1
                ):
                    # refer - https://github.com/BerriAI/reliableGPT/
                    # TODO: check the model being used and not always switch to 3.5 16k variant
                    payload.data["model"] = "gpt-3.5-turbo-16k"
                    logger.info(
                        f"Switching to 16k model for payload {payload.metadata['index']}"
                    )
                else:
                    payload.error = str(exc)
                    break

        return payload


class LLMMulticlient:
    """Uses asyncio to send requests to the OpenAI API concurrently."""

    def __init__(self, settings: t.Optional[Settings] = None):
        self._max_tries = 4
        self._rpm_limit = 10
        if settings is not None:
            openai.api_key = settings.check_and_get("openai_api_key")  # type: ignore
            self._rpm_limit = settings.check_and_get("openai_rpm_limit")

    def fetch_responses(self, input_payloads: list[Payload]) -> list[Payload]:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            logger.warning(
                "Detected a running event loop, scheduling requests in a separate thread."
            )
            with ThreadPoolExecutor(max_workers=1) as executor:
                return executor.submit(
                    asyncio.run, self.async_fetch_responses(input_payloads)
                ).result()
        else:
            return asyncio.run(self.async_fetch_responses(input_payloads))

    async def async_fetch_responses(
        self, input_payloads: list[Payload]
    ) -> list[Payload]:
        limiter = aiolimiter.AsyncLimiter(self._rpm_limit, time_period=1)
        async_outputs = [
            async_process_payload(data, limiter, self._max_tries)
            for data in input_payloads
        ]
        output_payloads = await tqdm_asyncio.gather(*async_outputs)
        return output_payloads
