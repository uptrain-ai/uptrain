import json
from unittest.mock import MagicMock, patch

import polars as pl

from uptrain.framework import Settings
from uptrain.operators import GrammarScore, LanguageCritique, ResponseCoherence
from uptrain.operators.language.llm import Payload


SETTINGS = Settings(model="ollama/llama3.2", evaluate_locally=True)


class _FakeChoice:
    def __init__(self, content: str):
        self.message = MagicMock()
        self.message.content = content


class _FakeResponse:
    def __init__(self, content: str):
        self.choices = [_FakeChoice(content)]


def _canned_fetch(input_payloads, validate_func=None):
    """Return a grade that satisfies the eval's validation function.

    LanguageCritique expects ``{"Score": <1-5>, "Reasoning": ...}`` while
    ResponseCoherence expects ``{"Choice": "A"|"B"|"C", "Reasoning": ...}``,
    so fall back to the Choice shape when the validator rejects the Score one.
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
        response = _FakeResponse(content)
        payloads.append(
            Payload(
                data={},
                metadata={"index": index},
                response=response,
            )
        )
    return payloads


def _score_columns(df: pl.DataFrame):
    return [col for col in df.columns if str(col).startswith("score_")]


# uptrain.operators.language.language_quality
def test_language_evals_return_nonnone_scores():
    df = pl.DataFrame(
        {"response": ["The Eiffel Tower is in Paris. It was completed in 1889."]}
    )
    evals = [
        LanguageCritique(),
        ResponseCoherence(),
    ]
    for op in evals:
        op.setup(SETTINGS)
        with patch(
            "uptrain.operators.language.llm.LLMMulticlient.fetch_responses",
            side_effect=_canned_fetch,
        ):
            output = op.run(df)["output"]

        columns = _score_columns(output)
        assert columns, f"{type(op).__name__} produced no score columns"
        for column in columns:
            assert output[column][0] is not None, (
                f"{type(op).__name__} returned a None result for {column!r}"
            )


# uptrain.operators.language.language_quality (multiple rows)
def test_language_evals_score_every_row():
    df = pl.DataFrame(
        {
            "response": [
                "The Eiffel Tower is in Paris and was completed in 1889.",
                "Sales went up last quarter because the team shipped on time.",
            ]
        }
    )
    op = ResponseCoherence().setup(SETTINGS)
    with patch(
        "uptrain.operators.language.llm.LLMMulticlient.fetch_responses",
        side_effect=_canned_fetch,
    ):
        output = op.run(df)["output"]

    column = "score_response_coherence"
    assert column in output.columns
    assert all(output[column][row] is not None for row in range(output.height))


# uptrain.operators.language.grammar
def test_grammar_score_returns_nonnone_result():
    df = pl.DataFrame({"text": ["The the the doubl word."]})
    op = GrammarScore().setup(SETTINGS)

    def _canned_number_fetch(input_payloads, validate_func=None):
        payloads = []
        for index in range(len(input_payloads)):
            response = _FakeResponse("95")
            payloads.append(
                Payload(data={}, metadata={"index": index}, response=response)
            )
        return payloads

    with patch(
        "uptrain.operators.language.llm.LLMMulticlient.fetch_responses",
        side_effect=_canned_number_fetch,
    ):
        output = op.run(df)["output"]

    assert "grammar_score" in output.columns
    assert output["grammar_score"][0] is not None