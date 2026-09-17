import asyncio
import gc
import warnings

import pytest

from uptrain.operators.language.llm import LLMMulticlient


@pytest.fixture
def client(monkeypatch):
    """LLM client with async_fetch_responses stubbed to controlled behavior."""
    monkeypatch.setattr(LLMMulticlient, "__init__", lambda self: None)
    c = LLMMulticlient()
    return c


def test_success_without_running_loop(client, monkeypatch):
    sent = {}

    async def fake(self, payloads, validate_func=None):
        sent["payloads"] = payloads
        sent["validate_func"] = validate_func
        return list(payloads)

    monkeypatch.setattr(LLMMulticlient, "async_fetch_responses", fake)
    assert client.fetch_responses(["a", "b"]) == ["a", "b"]
    assert sent["payloads"] == ["a", "b"]
    assert sent["validate_func"] is None


def test_success_inside_running_loop(client, monkeypatch):
    async def fake(self, payloads, validate_func=None):
        await asyncio.sleep(0)
        return list(payloads)

    monkeypatch.setattr(LLMMulticlient, "async_fetch_responses", fake)

    async def main():
        return client.fetch_responses(["x"])

    assert asyncio.run(main()) == ["x"]


@pytest.mark.parametrize("exc", [ValueError("boom"), RuntimeError("loop died")])
def test_exceptions_propagate_no_running_loop(client, monkeypatch, exc):
    async def fake(self, payloads, validate_func=None):
        raise exc

    monkeypatch.setattr(LLMMulticlient, "async_fetch_responses", fake)
    with pytest.raises(type(exc), match="boom|loop died"):
        client.fetch_responses(["p"])


@pytest.mark.parametrize("exc", [ValueError("boom"), RuntimeError("loop died")])
def test_exceptions_propagate_inside_running_loop(client, monkeypatch, exc):
    async def fake(self, payloads, validate_func=None):
        raise exc

    monkeypatch.setattr(LLMMulticlient, "async_fetch_responses", fake)

    async def main():
        with pytest.raises(type(exc), match="boom|loop died"):
            client.fetch_responses(["p"])

    asyncio.run(main())


def test_validate_func_forwarded(client, monkeypatch):
    seen = {}

    async def fake(self, payloads, validate_func=None):
        seen["v"] = validate_func
        return list(payloads)

    monkeypatch.setattr(LLMMulticlient, "async_fetch_responses", fake)
    marker = object()
    client.fetch_responses(["p"], validate_func=marker)
    assert seen["v"] is marker


def test_no_unawaited_coroutine_warning(client, monkeypatch):
    # async_fetch_responses raising after the coroutine was created must not
    # leave an un-awaited coroutine behind in either execution mode.
    async def fake(self, payloads, validate_func=None):
        raise ValueError("boom")

    monkeypatch.setattr(LLMMulticlient, "async_fetch_responses", fake)

    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        with pytest.raises(ValueError):
            client.fetch_responses(["p"])

    async def main():
        with warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            with pytest.raises(ValueError):
                client.fetch_responses(["p"])

    asyncio.run(main())
    gc.collect()
