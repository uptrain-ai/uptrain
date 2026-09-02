# Smoke tests for the ContentCoherence operator (long-form content coherence).
#
# ContentCoherence evaluates whether a long-form article keeps consistent
# terminology across sections. These tests drive the operator through its real
# prompt construction -> validation -> score extraction path with a mocked LLM,
# so they are deterministic and need no API key or network access.

import json
from unittest.mock import MagicMock, patch

import polars as pl

from uptrain.framework import Settings
from uptrain.framework.evals import Evals
from uptrain.operators.language.content_coherence import ContentCoherence
from uptrain.operators.language.llm import Payload


class _FakeChoice:
    def __init__(self, content: str):
        self.message = MagicMock()
        self.message.content = content


class _FakeResponse:
    def __init__(self, content: str):
        self.choices = [_FakeChoice(content)]


def _fake_fetch(input_payloads, validate_func=None):
    """Return a grade that satisfies ContentCoherence's validation function.

    The operator expects ``{"Choice": "A"|"B"|"C", ...}``. Always return a
    valid Choice grade so the score extraction runs for every row.
    """
    reply = '{"Choice": "C", "Reasoning": "Article drifts between terms."}'
    return [
        Payload(data={}, metadata={"index": i}, response=_FakeResponse(reply))
        for i in range(len(input_payloads))
    ]


def _run_content_coherence(rows, scenario_description=None, eval_type="cot"):
    settings = Settings(
        model="ollama/llama3.2",
        evaluate_locally=True,
        openai_api_key=None,
        eval_type=eval_type,
    )
    operator = ContentCoherence(
        scenario_description=scenario_description or "The article is about American soccer."
    )
    operator.setup(settings)
    data = pl.DataFrame({"response": rows})
    with patch(
        "uptrain.operators.language.llm.LLMMulticlient.fetch_responses",
        side_effect=_fake_fetch,
    ):
        return operator.run(data)["output"]


def test_content_coherence_produces_score_and_explanation():
    result = _run_content_coherence(
        ["Soccer is popular. Football has many fans. Soccer teams draw crowds."]
    )
    row = result.to_dicts()[0]
    assert row["score_content_coherence"] == 0.0  # Choice C -> 0.0
    assert row["explanation_content_coherence"]  # explanation is populated


def test_content_coherence_maps_a_grade_to_full_score():
    def graded_fetch(input_payloads, validate_func=None):
        reply = '{"Choice": "A", "Reasoning": "Consistent terminology."}'
        return [
            Payload(data={}, metadata={"index": i}, response=_FakeResponse(reply))
            for i in range(len(input_payloads))
        ]

    settings = Settings(model="ollama/llama3.2", evaluate_locally=True, openai_api_key=None)
    operator = ContentCoherence(scenario_description="The article is about American soccer.")
    operator.setup(settings)
    with patch(
        "uptrain.operators.language.llm.LLMMulticlient.fetch_responses",
        side_effect=graded_fetch,
    ):
        result = operator.run(pl.DataFrame({"response": ["An article with no drift."]}))["output"]
    assert result.to_dicts()[0]["score_content_coherence"] == 1.0  # Choice A -> 1.0


def test_content_coherence_supported_as_managed_eval():
    from uptrain.framework.evalllm import EVAL_TO_OPERATOR_MAPPING

    assert Evals.CONTENT_COHERENCE in EVAL_TO_OPERATOR_MAPPING
    assert isinstance(EVAL_TO_OPERATOR_MAPPING[Evals.CONTENT_COHERENCE], ContentCoherence)


def test_content_coherence_scores_multiple_rows():
    with patch(
        "uptrain.operators.language.llm.LLMMulticlient.fetch_responses",
        side_effect=_fake_fetch,
    ):
        result = _run_content_coherence(
            [
                "Soccer is popular. Football has many fans.",
                "The soccer season starts in February.",
            ]
        )
    scores = [row["score_content_coherence"] for row in result.to_dicts()]
    assert len(scores) == 2
    assert all(score is not None for score in scores)