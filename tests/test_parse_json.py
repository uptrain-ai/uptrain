# Tests for parse_json in uptrain/operators/language/llm.py.
#
# parse_json extracts the JSON object from an LLM reply. Models sometimes
# return an empty or brace-less reply, which previously triggered a misleading
# "Empty strings are not legal JSON5" error during parsing. These tests pin the
# graceful-handling behavior.

import pytest

from uptrain.operators.language.llm import parse_json


def test_parse_json_parses_object_reply():
    assert parse_json('{"Score": 5}') == {"Score": 5}


def test_parse_json_extracts_json_embedded_in_text():
    reply = 'Sure! Here is the result: {"Score": 4, "Reasoning": "Looks good."}'
    assert parse_json(reply) == {"Score": 4, "Reasoning": "Looks good."}


def test_parse_json_returns_empty_dict_for_empty_reply():
    assert parse_json("") == {}


def test_parse_json_returns_empty_dict_for_whitespace_reply():
    assert parse_json("   \n  ") == {}


def test_parse_json_returns_empty_dict_when_no_braces():
    assert parse_json("No JSON here, just prose.") == {}


def test_parse_json_returns_empty_dict_for_brace_less_content():
    # e.g. a reply that is a bare list rather than an object
    assert parse_json("[1, 2, 3]") == {}


def test_parse_json_returns_empty_dict_for_none():
    assert parse_json(None) == {}