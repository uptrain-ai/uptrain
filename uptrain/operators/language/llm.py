"""
Implement checks to test language quality. 
"""

from __future__ import annotations
import asyncio
from concurrent.futures import ThreadPoolExecutor
import random
import typing as t

from loguru import logger
from pydantic import BaseModel, Field

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.utilities import lazy_load_dep

openai = lazy_load_dep("openai", "openai")
litellm = lazy_load_dep("litellm", "litellm")
aiolimiter = lazy_load_dep("aiolimiter", "aiolimiter>=1.1")
tqdm_asyncio = lazy_load_dep("tqdm.asyncio", "tqdm>=4.0")


from openai import AsyncOpenAI
from openai import AsyncAzureOpenAI
import openai
#import openai.error


# -----------------------------------------------------------
# Make concurrent requests to the OpenAI or another LLM API
#
# Credits: https://github.com/cozodb/openai-multi-client/
# Seems to get stuck for me though.
# And zenoml code - https://github.com/zeno-ml/zeno-build/blob/main/zeno_build/models/providers/openai_utils.py
# -----------------------------------------------------------


class Payload(BaseModel):
    data: dict
    metadata: dict = Field(default_factory=dict)
    response: t.Any = None
    error: t.Optional[str] = None


async def async_process_payload(
    payload: Payload,
    rpm_limiter: aiolimiter.AsyncLimiter,
    tpm_limiter: aiolimiter.AsyncLimiter,
    aclient: t.Union[AsyncOpenAI, AsyncAzureOpenAI, None],
    max_retries: int,
) -> Payload:
    messages = payload.data["messages"]
    total_chars = sum(len(msg["role"]) + len(msg["content"]) for msg in messages)
    total_tokens = total_chars // 3  # average token length is 3, conservatively
    await rpm_limiter.acquire(1)
    # TODO: we should also count the response tokens, but this is a good baseline
    # since our use-case is evaluations mostly, not generation
    await tpm_limiter.acquire(total_tokens)

    for count in range(max_retries):  # failed requests don't count towards rate limit
        try:
            if aclient is not None:
                payload.response = await aclient.chat.completions.create(**payload.data, timeout=180)
            else:
                payload.response = await litellm.acompletion(
                    **payload.data,
                )
            break
        except Exception as exc:
            logger.error(f"Error when sending request to LLM API: {exc}")
            if (
                isinstance(
                    exc,
                    (
                        litellm.RateLimitError,
                        litellm.llms.azure.AzureOpenAIError,
                        openai.APIConnectionError,
                        openai.APITimeoutError,
                        openai.RateLimitError,
                        openai.InternalServerError,
                        openai.APIError,
                        openai.Timeout
                    ),
                )
                and count < max_retries - 1
            ):
                await asyncio.sleep(random.uniform(5, 30) * count + 60)
            elif (
                isinstance(exc, openai.BadRequestError)
                and exc.code is not None 
                and "context_length" in exc.code
                and count < max_retries - 1
            ):
                # refer - https://github.com/BerriAI/reliableGPT/
                # if required to set token limit - https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions#managing-conversations

                fallback = {
                    "gpt-3.5-turbo": "gpt-3.5-turbo-16k",
                    "gpt-3.5-turbo-0613": "gpt-3.5-turbo-16k-0613",
                    "gpt-3.5-turbo-16k": "claude-instant-1.2",
                    "gpt-3.5-turbo-16k-0613": "claude-instant-1.2",
                    "gpt-4": "gpt-4-32k",
                    "gpt-4-0613": "gpt-4-32k-0613",
                    "gpt-4-32k": "claude-2.0",
                    "gpt-4-32k-0613": "claude-2.0",
                }
                if payload.data["model"] in fallback.keys():
                    payload.data["model"] = fallback[payload.data["model"]]
                    logger.info(
                        f"Switching to larger context model for payload {payload.metadata['index']}"
                    )
            else:
                payload.error = str(exc)
                break

    return payload


class LLMMulticlient:
    """Uses asyncio to send requests to LLM APIs concurrently."""

    def __init__(self, settings: t.Optional[Settings] = None):
        self._max_tries = 4
        # TODO: consult for accurate limits - https://platform.openai.com/account/rate-limits
        self._rpm_limit = 200
        self._tpm_limit = 90_000
        self.aclient = None
        if settings is not None:
            if settings.model.startswith("gpt") and settings.check_and_get("openai_api_key") is not None:
                openai.api_key = settings.check_and_get("openai_api_key")  # type: ignore
                self.aclient = AsyncOpenAI()

            if settings.model.startswith("azure") and settings.check_and_get("azure_api_key") is not None:
                self.aclient = AsyncAzureOpenAI(
                    api_key = settings.azure_api_key,  
                    api_version=settings.azure_api_version,
                    azure_endpoint = settings.azure_api_base
                )

            self._rpm_limit = settings.check_and_get("rpm_limit")
            self._tpm_limit = settings.check_and_get("tpm_limit")

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
        rpm_limiter = aiolimiter.AsyncLimiter(self._rpm_limit, time_period=60)
        tpm_limiter = aiolimiter.AsyncLimiter(self._tpm_limit, time_period=60)
        async_outputs = [
            async_process_payload(data, rpm_limiter, tpm_limiter, self.aclient, self._max_tries)
            for data in input_payloads
        ]
        output_payloads = await tqdm_asyncio.tqdm_asyncio.gather(*async_outputs)
        return output_payloads
