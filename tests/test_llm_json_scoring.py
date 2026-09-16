# Regression tests for issues #725 and #726.
#
# Scoring code in the language operators used strict ``json.loads`` on raw LLM
# replies, while request validation already used the tolerant ``parse_json``.
# Providers such as Bedrock Claude wrap the JSON payload in prose or markdown
# fences, so validation passed but scoring raised, nulling scores with
# "Error when processing payload". These tests pin the tolerant scoring path.

import json

import pytest

from uptrain.operators.language.llm import parse_llm_choice, run_validation

FENCED_REPLY = (
    "Sure! Here is my judgement:\n"
    "```json\n"
    '{"Choice": "A",}\n'
    "```\n"
    "That is all."
)

PROSE_PREFIXED_REPLY = 'After reviewing the response, my verdict is {"Choice": "B"}.'

BARE_REPLY = '{"Choice": "A"}'


def score_choice(reply, score_mapping):
    """Mirror of the operator scoring loops (e.g. response_quality)."""
    try:
        return float(score_mapping[parse_llm_choice(reply)])
    except Exception:
        return None


def test_strict_json_loads_rejects_fenced_reply():
    # Documents the reported bug: strict parsing cannot handle real replies.
    with pytest.raises(json.JSONDecodeError):
        json.loads(FENCED_REPLY)["Choice"]


def test_parse_llm_choice_extracts_fenced_reply():
    assert parse_llm_choice(FENCED_REPLY) == "A"


def test_parse_llm_choice_extracts_prose_prefixed_reply():
    assert parse_llm_choice(PROSE_PREFIXED_REPLY) == "B"


def test_parse_llm_choice_tolerates_trailing_comma():
    assert parse_llm_choice('{"Choice": "A",}') == "A"


def test_parse_llm_choice_returns_none_for_empty_reply():
    assert parse_llm_choice("") is None


def test_parse_llm_choice_returns_none_for_none_reply():
    assert parse_llm_choice(None) is None


def test_parse_llm_choice_returns_none_when_choice_missing():
    assert parse_llm_choice('{"Score": 5}') is None


def test_scoring_recovers_fenced_reply():
    assert score_choice(FENCED_REPLY, {"A": 1.0, "B": 0.0}) == 1.0


def test_scoring_still_null_when_choice_missing():
    assert score_choice('{"Score": 5}', {"A": 1.0, "B": 0.0}) is None


def test_validation_and_scoring_agree():
    replies = [BARE_REPLY, FENCED_REPLY, PROSE_PREFIXED_REPLY]
    for reply in replies:
        assert run_validation(reply, lambda out: "Choice" in out) is True
        assert parse_llm_choice(reply) is not None
