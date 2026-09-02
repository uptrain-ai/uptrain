# Smoke tests for the managed evaluation runner (EvalLLM.evaluate).
#
# These cover the full managed-eval path: EvalLLM maps a named Evals check to
# its operator, runs prompt construction -> response validation -> score
# extraction, and returns per-row results. The LLM client is mocked so the
# tests are deterministic and need no API key or network access.
#
# The managed-eval operators import a number of optional/LLM packages at
# import time (e.g. rouge_score). Tests import them lazily and skip with a
# clear message when those are not installed, so collection never breaks on a
# minimal environment.

import json
from unittest.mock import MagicMock, patch

import pytest
import polars as pl

from uptrain.operators.language.llm import Payload


class _FakeChoice:
    def __init__(self, content: str):
        self.message = MagicMock()
        self.message.content = content


class _FakeResponse:
    def __init__(self, content: str):
        self.choices = [_FakeChoice(content)]


def _canned_fetch(input_payloads, validate_func=None):
    """Return a grade that satisfies the eval's validation function.

    Some managed evals expect ``{"Score": <1-5>, "Reasoning": ...}`` while
    others expect ``{"Choice": "A"|"B"|"C", "Reasoning": ...}``. Fall back to
    the Choice shape whenever the validator rejects the Score one.
    """
    score_reply = '{"Score": 5, "Reasoning": "Looks good."}'
    choice_reply = '{"Choice": "A", "Reasoning": "Looks good."}'
    content = choice_reply
    if validate_func is not None:
        try:
            accepted = validate_func(json.loads(score_reply))
        except Exception:
            accepted = False
        content = score_reply if accepted else choice_reply

    payloads = []
    for index in range(len(input_payloads)):
        payloads.append(
            Payload(
                data={},
                metadata={"index": index},
                response=_FakeResponse(content),
            )
        )
    return payloads


def _managed_evals():
    try:
        from uptrain.framework import EvalLLM
        from uptrain.framework.evals import Evals
        from uptrain.framework import Settings
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"Managed-eval dependencies are not installed: {exc}")

    settings = Settings(model="ollama/llama3.2", evaluate_locally=True, openai_api_key=None)
    evaluator = EvalLLM(settings=settings)
    return evaluator, Evals


def _question_response_data():
    return [
        {
            "question": "What is Paris famous for?",
            "response": "The Eiffel Tower is a famous wrought-iron lattice tower in Paris.",
            "context": "Paris is the capital of France and is known for the Eiffel Tower.",
        }
    ]


# uptrain.framework.EvalLLM.evaluate (managed evals)
def test_managed_evals_return_nonnone_scores_for_question_response_evals():
    evaluator, Evals = _managed_evals()
    data = _question_response_data()
    checks = [Evals.CRITIQUE_LANGUAGE, Evals.RESPONSE_RELEVANCE, Evals.RESPONSE_COMPLETENESS]

    with patch(
        "uptrain.operators.language.llm.LLMMulticlient.fetch_responses",
        side_effect=_canned_fetch,
    ):
        result = evaluator.evaluate(data=data, checks=checks, project_name="smoke")[0]

    score_columns = {key for key in result if key.startswith("score")}
    assert score_columns, "managed evals produced no score columns"
    assert all(result[key] is not None for key in score_columns)