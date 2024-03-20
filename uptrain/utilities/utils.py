from datetime import datetime
import os
import polars as pl

import fsspec
from fsspec.implementations.dirfs import DirFileSystem

from uptrain import (
    Evals,
    ResponseMatching,
    GuidelineAdherence,
    ConversationSatisfaction,
    JailbreakDetection,
    CritiqueTone,
)
from uptrain.utilities import lazy_load_dep

def check_openai_api_key(api_key):
    import openai
    client = openai.OpenAI(api_key=api_key)
    try:
        client.models.list()
    except openai.AuthenticationError:
        return False
    else:
        return True
    
def _get_fsspec_filesystem(database_path) -> fsspec.AbstractFileSystem:
    return DirFileSystem(database_path, auto_mkdir=True)

fsspec.config.conf["file"] = {"auto_mkdir": True}

evals_mapping = {
    "context_relevance": Evals.CONTEXT_RELEVANCE,
    "factual_accuracy": Evals.FACTUAL_ACCURACY,
    "response_relevance": Evals.RESPONSE_RELEVANCE,
    "critique_language": Evals.CRITIQUE_LANGUAGE,
    "response_completeness": Evals.RESPONSE_COMPLETENESS,
    "response_completeness_wrt_context": Evals.RESPONSE_COMPLETENESS_WRT_CONTEXT,
    "response_consistency": Evals.RESPONSE_CONSISTENCY,
    "response_conciseness": Evals.RESPONSE_CONCISENESS,
    "valid_response": Evals.VALID_RESPONSE,
    "response_alignment_with_scenario": Evals.RESPONSE_ALIGNMENT_WITH_SCENARIO,
    "response_sincerity_with_scenario": Evals.RESPONSE_SINCERITY_WITH_SCENARIO,
    "prompt_injection": Evals.PROMPT_INJECTION,
    "code_hallucination": Evals.CODE_HALLUCINATION,
    "sub_query_completeness": Evals.SUB_QUERY_COMPLETENESS,
    "context_reranking": Evals.CONTEXT_RERANKING,
    "context_conciseness ": Evals.CONTEXT_CONCISENESS,
}

parametric_evals_mapping = {
    "CritiqueTone": CritiqueTone,
    "GuidelineAdherence": GuidelineAdherence,
    "ConversationSatisfaction": ConversationSatisfaction,
    "ResponseMatching": ResponseMatching,
    "JailbreakDetection": JailbreakDetection,
}


def checks_mapping(check_name: str, params: dict = dict()):
    if check_name in evals_mapping:
        return evals_mapping[check_name]
    elif check_name in parametric_evals_mapping:
        return parametric_evals_mapping[check_name](**params)
    else:
        return None


def get_uuid():
    import uuid

    return str(uuid.uuid4().hex)


def get_current_datetime():
    return datetime.utcnow()


def hash_string(s: str):
    import hashlib

    return hashlib.sha256(s.encode()).hexdigest()


def create_dirs(path: str):
    dirs_to_create = [
        os.path.join(path),
        os.path.join(path, "uptrain-datasets"),
        os.path.join(path, "uptrain-eval-results"),
    ]
    for _dir in dirs_to_create:
        os.makedirs(_dir, exist_ok=True)
    return


def get_sqlite_utils_db(fpath: str):
    sqlite = lazy_load_dep("sqlite_utils", "sqlite_utils")
    import sqlite3

    conn = sqlite3.connect(fpath, check_same_thread=False)
    return sqlite.Database(conn)


def parse_prompt(prompt):
    prompt_vars = []
    if prompt is not None and len(prompt):
        if "{{" in prompt:
            prompt_vars = [x.split("}}")[0] for x in prompt.split("{{")[1:]]
            for var in prompt_vars:
                prompt = prompt.replace("{{" + var + "}}", "{" + var + "}")
        elif "{" in prompt:
            prompt_vars = [x.split("}")[0] for x in prompt.split("{")[1:]]
    else:
        prompt = ""
    return prompt, prompt_vars


def convert_project_to_polars(project_data):
    dictn = []
    for row in project_data:
        data = row["data"]
        data.update(row["checks"])
        if "uptrain_settings" in row["metadata"]:
            del row["metadata"]["uptrain_settings"]
        data.update(row["metadata"])
        data.update({"project_name": row["project"], "timestamp": row["timestamp"]})
        dictn.append(data)
    return pl.DataFrame(dictn)


def convert_project_to_dicts(project_data):
    dictn = []
    checks_mapping = {}
    for row in project_data:
        data = row["data"]
        # data.update(row['checks'])
        uuid_tag = get_uuid()
        data.update({"uuid_tag": uuid_tag})
        checks_mapping[uuid_tag] = row["checks"]
        if "uptrain_settings" in row["metadata"]:
            del row["metadata"]["uptrain_settings"]
        data.update(row["metadata"])
        data.update({"project_name": row["project"], "timestamp": row["timestamp"]})
        dictn.append(data)
    return pl.DataFrame(dictn), checks_mapping
