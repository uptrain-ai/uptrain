"""
Implement checks to test language quality. 
"""

from __future__ import annotations
import asyncio
from concurrent.futures import ThreadPoolExecutor
import random
import typing as t
import json5

from loguru import logger
from pydantic import BaseModel, Field

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.utilities import lazy_load_dep

openai = lazy_load_dep("openai", "openai")
aiolimiter = lazy_load_dep("aiolimiter", "aiolimiter>=1.1")
tqdm_asyncio = lazy_load_dep("tqdm.asyncio", "tqdm>=4.0")


from openai import AsyncOpenAI
from openai import AsyncAzureOpenAI
import openai
from aiolimiter import AsyncLimiter

# import openai.error


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


def parse_json(json_str: str) -> dict:
    first_brace_index = json_str.find('{')
    last_brace_index = json_str.rfind('}')
    json_str = json_str[first_brace_index:last_brace_index + 1]
    try:
        return json5.loads(json_str)
    except Exception as e:
        logger.error(f"Error when parsing JSON: {e}")
        return {}

def run_validation(llm_output, validation_func):
    llm_output = parse_json(llm_output)
    try:
        return validation_func(llm_output)
    except Exception as e:
        logger.error(f"Error when running validation function: {e}")
        return False


async def async_process_payload(
    payload: Payload,
    rpm_limiter: AsyncLimiter,
    tpm_limiter: AsyncLimiter,
    aclient: t.Any,
    max_retries: int,
    validate_func: t.Callable = None,
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
                payload.response = await aclient.chat.completions.create(
                    **payload.data, timeout=180
                )
            else:
                litellm = lazy_load_dep("litellm", "litellm")
                payload.response = await litellm.acompletion(
                    **payload.data,
                )
            if validate_func is not None:
                if not run_validation(
                    payload.response.choices[0].message.content, validate_func
                ):
                    raise Exception(
                        f"Response doesn't pass the validation func.\nResponse: {payload.response.choices[0].message.content}"
                    )
            break
        except Exception as exc:
            logger.error(f"Error when sending request to LLM API: {exc}")
            sleep_and_retry = count < max_retries - 1
            if aclient is not None:
                if not (
                    isinstance(
                        exc,
                        (
                            openai.APIConnectionError,
                            openai.APITimeoutError,
                            openai.InternalServerError,
                            openai.RateLimitError,
                            openai.UnprocessableEntityError,
                        ),
                    )
                ):
                    sleep_and_retry = False
            else:
                litellm = lazy_load_dep("litellm", "litellm")
                if not (
                    isinstance(
                        exc,
                        (litellm.RateLimitError,),
                    )
                ):
                    sleep_and_retry = False

            if sleep_and_retry:
                logger.info(
                    f"Going to sleep before retrying for payload {payload.metadata['index']}"
                )
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
            elif "Response doesn't pass the validation func" in str(exc):
                logger.info(f"Retrying for payload {payload.metadata['index']}")
            else:
                payload.error = str(exc)
                break

    return payload


class LLMMulticlient:
    """Uses asyncio to send requests to LLM APIs concurrently."""

    def __init__(self, settings: t.Optional[Settings] = None, aclient: t.Any = None):
        self._max_tries = 4
        # TODO: consult for accurate limits - https://platform.openai.com/account/rate-limits
        self._rpm_limit = 200
        self._tpm_limit = 90_000
        self.aclient = aclient
        self.settings = settings
        if settings is not None:
            if (
                settings.model.startswith("gpt")
                and settings.check_and_get("openai_api_key") is not None
            ):
                openai.api_key = settings.check_and_get("openai_api_key")  # type: ignore
                if self.aclient is None:
                    self.aclient = AsyncOpenAI()

            if (
                settings.model.startswith("azure")
                and settings.check_and_get("azure_api_key") is not None
            ):
                self.aclient = AsyncAzureOpenAI(
                    api_key=settings.azure_api_key,
                    api_version=settings.azure_api_version,
                    azure_endpoint=settings.azure_api_base,
                )

            if (
                settings.model.startswith("anyscale")
                and settings.check_and_get("anyscale_api_key") is not None
            ):
                self.aclient = AsyncOpenAI(
                    api_key=settings.anyscale_api_key,
                    base_url="https://api.endpoints.anyscale.com/v1",
                )
            if (
                settings.model.startswith("together")
                and settings.check_and_get("together_api_key") is not None
            ):
                self.aclient = AsyncOpenAI(
                    api_key=settings.together_api_key,
                    base_url="https://api.together.xyz/v1",
                )
            if (
                settings.model.startswith("ollama")
            ):
                self.aclient = None
            self._rpm_limit = settings.check_and_get("rpm_limit")
            self._tpm_limit = settings.check_and_get("tpm_limit")

    def make_payload(
        self,
        index: int,
        prompt: str,
        temperature: float = 0.1,
    ) -> Payload:
        model = self.settings.model
        seed = self.settings.seed
        response_format = self.settings.response_format

        prefixes = ["anyscale/", "azure/", "together/"]
        for prefix in prefixes:
            model = model.replace(prefix, "")

        messages = [{"role": "user", "content": prompt}]

        data = {"model": model, "messages": messages, "temperature": temperature}
        if seed is not None:
            data["seed"] = seed
        if response_format is not None:
            data["response_format"] = response_format
        return Payload(
            endpoint="chat.completions",
            data=data,
            metadata={"index": index},
        )

    def fetch_responses(
        self, input_payloads: list[Payload], validate_func: t.Callable = None
    ) -> list[Payload]:
        try:
            return asyncio.run(
                self.async_fetch_responses(input_payloads, validate_func=validate_func)
            )
        except Exception as e:
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    logger.warning(
                        "Detected a running event loop, scheduling requests in a separate thread."
                    )
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        return executor.submit(
                            asyncio.run,
                            self.async_fetch_responses(
                                input_payloads, validate_func=validate_func
                            ),
                        ).result()
            except Exception:
                logger.error(f"Caught an exception: {e}")

    async def async_fetch_responses(
        self,
        input_payloads: list[Payload],
        validate_func: t.Callable = None,
    ) -> list[Payload]:
        rpm_limiter = AsyncLimiter(self._rpm_limit, time_period=60)
        tpm_limiter = AsyncLimiter(self._tpm_limit, time_period=60)
        async_outputs = [
            async_process_payload(
                data,
                rpm_limiter,
                tpm_limiter,
                self.aclient,
                self._max_tries,
                validate_func=validate_func,
            )
            for data in input_payloads
        ]
        output_payloads = await tqdm_asyncio.tqdm_asyncio.gather(*async_outputs)
        return output_payloads
