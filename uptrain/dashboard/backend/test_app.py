"""Tests for the safe JSON parsing helper used by the dashboard backend.

These tests exercise the fix for GHSL-2024-200 / GHSL-2024-201, where
`eval()` was called directly on attacker-controlled form data (`checks`
and `metadata`) in the `/add_prompts` and `/new_run` endpoints (and
`/create_project`, and the `/projects` listing).
"""
import os

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

os.environ.setdefault("UPTRAIN_LOCAL_URL", "http://localhost:4300")

import app as backend_app

MALICIOUS_PAYLOAD = "__import__('os').system('touch /tmp/ghsl_2024_200_poc')"


def setup_function(_):
    # Make sure a previous (failed) exploit run doesn't leave a false positive
    if os.path.exists("/tmp/ghsl_2024_200_poc"):
        os.remove("/tmp/ghsl_2024_200_poc")


def test_parse_user_json_accepts_valid_list():
    assert backend_app._parse_user_json("[1, 2, 3]", "checks", expected_type=list) == [
        1,
        2,
        3,
    ]


def test_parse_user_json_accepts_valid_dict():
    assert backend_app._parse_user_json(
        '{"model": "gpt-4"}', "metadata", expected_type=dict
    ) == {"model": "gpt-4"}


def test_parse_user_json_falls_back_to_literal_eval():
    # Python-literal style (single quotes) is not valid JSON but is a safe literal.
    assert backend_app._parse_user_json("['a', 'b']", "checks", expected_type=list) == [
        "a",
        "b",
    ]


def test_parse_user_json_rejects_malicious_payload():
    with pytest.raises(HTTPException) as excinfo:
        backend_app._parse_user_json(MALICIOUS_PAYLOAD, "metadata", expected_type=dict)
    assert excinfo.value.status_code == 400
    assert not os.path.exists("/tmp/ghsl_2024_200_poc")


def test_parse_user_json_rejects_wrong_type():
    with pytest.raises(HTTPException) as excinfo:
        backend_app._parse_user_json("123", "checks", expected_type=list)
    assert excinfo.value.status_code == 400


def test_parse_user_json_rejects_malformed_input():
    with pytest.raises(HTTPException) as excinfo:
        backend_app._parse_user_json("{not valid", "metadata", expected_type=dict)
    assert excinfo.value.status_code == 400


@pytest.fixture()
def client():
    return TestClient(backend_app.app, raise_server_exceptions=False)


def _post_add_prompts(client, checks, metadata):
    return client.post(
        "/api/public/add_prompts",
        headers={"uptrain-access-token": "default_key"},
        data={
            "project_id": "does-not-exist",
            "model": "gpt-4",
            "dataset_name": "dataset",
            "prompt": "hello {var}",
            "checks": checks,
            "metadata": metadata,
            "prompt_name": "prompt",
        },
        files={"data_file": ("data.jsonl", b"", "application/octet-stream")},
    )


def _post_new_run(client, checks, metadata):
    return client.post(
        "/api/public/new_run",
        headers={"uptrain-access-token": "default_key"},
        data={
            "model": "gpt-4",
            "dataset_name": "dataset",
            "evaluation_name": "eval",
            "checks": checks,
            "project_id": "does-not-exist",
            "metadata": metadata,
        },
        files={"data_file": ("data.jsonl", b"", "application/octet-stream")},
    )


def test_add_prompts_rejects_malicious_metadata(client):
    resp = _post_add_prompts(client, checks=["some_check"], metadata=MALICIOUS_PAYLOAD)
    assert resp.status_code == 400
    assert not os.path.exists("/tmp/ghsl_2024_200_poc")


def test_add_prompts_rejects_malicious_checks(client):
    resp = _post_add_prompts(client, checks=[MALICIOUS_PAYLOAD], metadata="{}")
    assert resp.status_code == 400
    assert not os.path.exists("/tmp/ghsl_2024_200_poc")


def test_new_run_rejects_malicious_metadata(client):
    resp = _post_new_run(client, checks=["some_check"], metadata=MALICIOUS_PAYLOAD)
    assert resp.status_code == 400
    assert not os.path.exists("/tmp/ghsl_2024_200_poc")


def test_new_run_rejects_malicious_checks(client):
    resp = _post_new_run(client, checks=[MALICIOUS_PAYLOAD], metadata="{}")
    assert resp.status_code == 400
    assert not os.path.exists("/tmp/ghsl_2024_200_poc")


def test_add_prompts_valid_json_passes_parsing(client):
    # Valid JSON payloads must not be rejected as malformed input: parsing
    # should succeed and the request should fail later (if at all) for
    # unrelated reasons (e.g. missing project), never with our 400 for
    # "could not parse value".
    resp = _post_add_prompts(client, checks='["some_check"]', metadata="{}")
    assert resp.status_code != 400 or "could not parse value" not in resp.text


def test_new_run_valid_json_passes_parsing(client):
    resp = _post_new_run(client, checks='["some_check"]', metadata="{}")
    assert resp.status_code != 400 or "could not parse value" not in resp.text
