"""Uptrain server to receive evaluation requests from clients, and 
schedule them on execute. 
 
NOTE: Make sure all public api methods make use of `user_name` to only 
work with rows specific to the user.
"""

from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime, timedelta
import datetime as dt
import json
import io
import os
import typing as t
import uvicorn
import polars as pl
import sys

from uptrain.framework import Settings, EvalLLM
from uptrain.operators import ColumnOp, ColumnOp, Table, LineChart, Histogram

import pandas as pd
import dateutil.parser

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    HTTPException,
    UploadFile,
    Form,
    File,
    Security,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader


from loguru import logger
from sqlalchemy.orm import Session

from uptrain.utilities.db import create_database, ModelDataset, ModelUser, ModelPrompt
from uptrain.utilities.utils import (
    get_sqlite_utils_db,
    _get_fsspec_filesystem,
    convert_project_to_polars,
    convert_project_to_dicts,
    checks_mapping,
    create_dirs,
    get_current_datetime,
)
from uptrain.utilities import polars_to_pandas

from uptrain.utilities import app_schema


def _row_to_dict(row):
    return {k: v for k, v in row.__dict__.items() if not k.startswith("_")}


# -----------------------------------------------------------
# Dependencies
# -----------------------------------------------------------

DATABASE_PATH = "/data/uptrain_data/"
# security
ACCESS_TOKEN = APIKeyHeader(name="uptrain-access-token", auto_error=False)

# database
# /data/uptrain-server.db"
create_dirs(DATABASE_PATH)
SessionLocal = create_database("sqlite:///" + DATABASE_PATH + "uptrain-local-server.db")


def _create_user(db: Session, name: str):
    """Create a new user."""
    db_user = ModelUser(name=name)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as exc:
        db.rollback()
        raise exc


def get_db():
    """Get the database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        SessionLocal.remove()


try:
    _create_user(SessionLocal(), "default_key")
except Exception:
    pass

# some methods need a context manager to get the db
get_db_context = contextmanager(get_db)


def get_fsspec_fs():
    """Get the fsspec filesystem object."""
    try:
        yield _get_fsspec_filesystem(DATABASE_PATH)
    finally:
        pass


async def validate_api_key_public(key_header: str = Security(ACCESS_TOKEN)) -> str:
    """Validate API key and return the user id.

    For public API, the API key is the access token provided to them by uptrain and we
    deduce the user name from the access token. For admin access, the user name is
    provided in another header.
    """
    if key_header is None:
        raise HTTPException(status_code=403, detail="Unspecified API key")
    else:
        with get_db_context() as db:
            db_item = db.query(ModelUser).filter_by(name=key_header).first()
            if db_item is not None:
                return db_item.id
            else:
                raise HTTPException(status_code=403, detail="Invalid API key")


# -----------------------------------------------------------
# Routers
# -----------------------------------------------------------

router_public = APIRouter(dependencies=[Depends(validate_api_key_public)])
router_internal = APIRouter()

# -----------------------------------------------------------
# Internal API
# -----------------------------------------------------------


@router_internal.post("/user")
def add_user(user: app_schema.UserCreate, db: Session = Depends(get_db)):
    """Add a new user."""
    name = user.name
    try:
        db_user = _create_user(db, name)
        return db_user
    except Exception as exc:
        logger.exception(exc)
        raise HTTPException(status_code=400, detail=f"Error creating user: {name}")


# -----------------------------------------------------------
# Public API
# -----------------------------------------------------------

# -----------------------------------------------------------
# User management
# -----------------------------------------------------------


# Request to get user name, API key, user credits used and total using api key
@router_public.post("/user")
def get_user(
    user_id: str = Depends(validate_api_key_public), db: Session = Depends(get_db)
):
    user = db.query(ModelUser).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        return {
            "id": user_id,
            "user_name": "open-source user",
            "api_key": "default_key",
        }


@router_public.get("/get_project_data", response_model=app_schema.ProjectData)
def get_project_data(
    project_name: str,
    num_days: int = 7,
    db: Session = Depends(get_db),
    user_id: str = Depends(validate_api_key_public),
):
    """Get all the data for a particular project_name for the given user."""
    projects = get_projects_list(num_days=num_days, db=db, user_id=user_id)

    for project in projects.data:
        if project["project"] == project_name:
            run_via = project["run_via"]
            if run_via == "project" or run_via == "experiment":
                if run_via == "project":
                    query = f"""
                        SELECT *
                        FROM results
                        WHERE project = '{project_name}' AND metadata NOT LIKE '%prompt_version%' AND metadata NOT LIKE '%uptrain_experiment_columns%' AND timestamp > datetime('now', '-{num_days} days')
                        """
                else:
                    query = f"""
                        SELECT *
                        FROM results
                        WHERE project = '{project_name}' AND metadata LIKE '%uptrain_experiment_columns%' AND timestamp > datetime('now', '-{num_days} days')
                        """
                fpath = os.path.join(
                    DATABASE_PATH, "uptrain-eval-results", f"{user_id}.db"
                )
                if not os.path.exists(fpath):
                    raise HTTPException(
                        status_code=404, detail="No evaluations run yet for this user"
                    )
                DB = get_sqlite_utils_db(fpath)

                buffer = io.StringIO()
                for row in DB.query(query):
                    buffer.write(json.dumps(row) + "\n")
                buffer.seek(0)
                data = []
                for line in buffer:
                    details = json.loads(line)
                    for key in details:
                        try:
                            details[key] = json.loads(details[key])
                        except Exception:
                            pass
                    data.append(details)
                scores = [
                    col[6:]
                    for col in data[0]["checks"].keys()
                    if col.startswith("score_")
                ]
                if run_via == "project":
                    return app_schema.ProjectData(
                        data=[
                            data,
                            None,
                            project["latest_timestamp"][:10],
                            None,
                            scores,
                        ],
                        project_name=project_name,
                    )
                else:
                    exp_data = convert_project_to_polars(data)
                    exp_column = str(exp_data["uptrain_experiment_columns"][0][0])

                    plot_data = {}
                    for col in scores:
                        col_name = "score_" + col
                        plot_data.update(
                            {
                                col: exp_data.group_by(
                                    [exp_column], maintain_order=True
                                )
                                .agg(pl.col(col_name))
                                .to_dicts()
                            }
                        )

                    columns = exp_data.columns
                    columns.remove("question")
                    display_data = (
                        exp_data.group_by(["question"], maintain_order=True)
                        .agg(pl.col(col) for col in columns)
                        .to_dicts()
                    )
                    unqiue_values = list(set(exp_data[exp_column].to_list()))
                    return app_schema.ProjectData(
                        data=[
                            display_data,
                            None,
                            project["latest_timestamp"][:10],
                            None,
                            scores,
                            unqiue_values,
                            exp_column,
                            plot_data,
                        ],
                        project_name=project_name,
                    )


@router_public.get("/get_prompt_data", response_model=app_schema.ProjectData)
def get_prompt_data(
    project_name: str,
    num_days: int = 7,
    db: Session = Depends(get_db),
    user_id: str = Depends(validate_api_key_public),
):
    """Get all the data for a particular project_name for the given user."""
    projects = get_projects_list(num_days=num_days, db=db, user_id=user_id)

    for project in projects.data:
        if project["project"] == project_name:
            run_via = project["run_via"]
            if run_via == "prompt":
                query = f"""
                    SELECT *
                    FROM results
                    WHERE project = '{project_name}' AND metadata like '%prompt_version%' AND metadata NOT LIKE '%uptrain_experiment_columns%' AND timestamp > datetime('now', '-{num_days} days')
                    """
                fpath = os.path.join(
                    DATABASE_PATH, "uptrain-eval-results", f"{user_id}.db"
                )
                if not os.path.exists(fpath):
                    raise HTTPException(
                        status_code=404, detail="No evaluations run yet for this user"
                    )
                DB = get_sqlite_utils_db(fpath)

                buffer = io.StringIO()
                for row in DB.query(query):
                    buffer.write(json.dumps(row) + "\n")
                buffer.seek(0)
                data = []
                for line in buffer:
                    details = json.loads(line)
                    for key in details:
                        try:
                            details[key] = json.loads(details[key])
                        except Exception:
                            pass
                    data.append(details)

                exp_data, checks_mapping = convert_project_to_dicts(data)

                columns = exp_data.columns
                columns.remove("prompt_name")
                columns.remove("prompt_version")
                data = exp_data.group_by(
                    ["prompt_name", "prompt_version"], maintain_order=True
                ).agg(pl.col(col) for col in columns)
                columns = data.columns
                columns.remove("prompt_name")
                data = (
                    data.group_by(["prompt_name"], maintain_order=True)
                    .agg(pl.col(col) for col in columns)
                    .to_dicts()
                )

                for row in data:
                    row["scores"] = []
                    uuid_tags_version = row["uuid_tag"]
                    for uuid_tags in uuid_tags_version:
                        scores = []
                        for uuid in uuid_tags:
                            score = checks_mapping[uuid]
                            scores.append(score)
                        row["scores"].append(pl.DataFrame(scores).mean().to_dicts()[0])

                res = []
                for prompt in data:
                    prompt_data = []
                    num_versions = len(prompt["prompt_version"])
                    for i in range(num_versions):
                        prompt_v = {}
                        for key, value in prompt.items():
                            # Return only one string instead of a list of strings
                            if key == "prompt":
                                value = value[i]
                            # Remove the explanations from the scores
                            elif key == "scores":
                                try:
                                    value = [
                                        {
                                            k: round(float(v), 3)
                                            for k, v in score.items()
                                            if not k.startswith("explanation")
                                        }
                                        for score in value
                                    ]
                                except Exception:
                                    value = [
                                        {
                                            k: v
                                            for k, v in score.items()
                                            if not k.startswith("explanation")
                                        }
                                        for score in value
                                    ]
                            # Handle cases where the value is a list or a string
                            if isinstance(value, list):
                                prompt_v[key] = value[i]
                            else:
                                prompt_v[key] = value
                        prompt_data.append(prompt_v)
                    res.append(
                        {"prompt_name": prompt["prompt_name"], "prompts": prompt_data}
                    )
                return app_schema.ProjectData(data=res, project_name=project_name)


@router_public.post("/add_project_data")
async def add_project_data(
    eval_args: app_schema.EvaluateV2,
    user_id: str = Depends(validate_api_key_public),
    db: Session = Depends(get_db),
):

    fpath = os.path.join(DATABASE_PATH, "uptrain-eval-results", f"{user_id}.db")
    DB = get_sqlite_utils_db(fpath)

    metadata = eval_args.metadata
    schema = eval_args.schema_dict
    results = eval_args.data
    checks = eval_args.checks
    project = eval_args.project
    timestamp = get_current_datetime()
    try:
        DB["results"].insert_all(
            [
                {
                    "data": row_data,
                    "checks": row_check,
                    "metadata": metadata,
                    "schema": schema,
                    "project": project,
                    "timestamp": timestamp,
                }
                for row_data, row_check in zip(results, checks)
            ]
        )
    except Exception as e:
        logger.exception(f"Error running the eval: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error saving the data for the project: {e}"
        )


@router_public.get("/get_projects_list", response_model=app_schema.ProjectsList)
def get_projects_list(
    num_days: int = 200,
    active_only: bool = True,
    limit: int = 10,
    db: Session = Depends(get_db),
    user_id: str = Depends(validate_api_key_public),
):
    """Get all the project names associated with the user."""
    user = db.query(ModelUser).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(status_code=403, detail="Invalid user name")
    else:
        user_name = user.name
    try:
        query = f"""
        SELECT project, MAX(timestamp) AS latest_timestamp
        FROM results
        WHERE metadata LIKE '%uptrain_experiment_columns%' AND timestamp > datetime('now', '-{num_days} days')
        GROUP BY project
        ORDER BY latest_timestamp DESC
        LIMIT {limit}
        """
        fpath = os.path.join(DATABASE_PATH, "uptrain-eval-results", f"{user_id}.db")
        if not os.path.exists(fpath):
            raise HTTPException(
                status_code=404, detail="No evaluations run yet for this user"
            )
        DB = get_sqlite_utils_db(fpath)

        experiment_runs = DB.query(query)
    except Exception:
        experiment_runs = []

    try:
        query = f"""
        SELECT project, MAX(timestamp) AS latest_timestamp
        FROM results
        WHERE metadata NOT LIKE '%prompt_version%' AND metadata NOT LIKE '%uptrain_experiment_columns%' AND timestamp > datetime('now', '-{num_days} days')
        GROUP BY project
        ORDER BY latest_timestamp DESC
        LIMIT {limit}
        """
        fpath = os.path.join(DATABASE_PATH, "uptrain-eval-results", f"{user_id}.db")
        if not os.path.exists(fpath):
            raise HTTPException(
                status_code=404, detail="No evaluations run yet for this user"
            )
        DB = get_sqlite_utils_db(fpath)

        project_runs = DB.query(query)
    except Exception:
        project_runs = []

    try:
        prompts_runs = get_prompts_list(
            num_days=num_days, limit=limit, db=db, user_id=user_id
        )
    except Exception:
        prompts_runs = []

    out = []

    for run in project_runs:
        out.append(
            {
                "project": run["project"],
                "latest_timestamp": run["latest_timestamp"],
                "run_via": "project",
            }
        )

    for run in experiment_runs:
        out.append(
            {
                "project": run["project"],
                "latest_timestamp": run["latest_timestamp"],
                "run_via": "experiment",
            }
        )

    for run in prompts_runs.data:
        out.append(
            {
                "project": run["project"],
                "latest_timestamp": run["latest_timestamp"],
                "run_via": "prompt",
            }
        )

    out.sort(reverse=True, key=lambda x: x["latest_timestamp"])
    return app_schema.ProjectsList(data=out, user_name=user_name)


@router_public.get("/get_evaluations_list", response_model=app_schema.ProjectsList)
def get_evaluations_list(
    num_days: int = 200,
    active_only: bool = True,
    limit: int = 10,
    db: Session = Depends(get_db),
    user_id: str = Depends(validate_api_key_public),
):
    """Get all the project names associated with the user."""
    user = db.query(ModelUser).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(status_code=403, detail="Invalid user name")
    else:
        user_name = user.name

    try:
        query = f"""
        SELECT project, MAX(timestamp) AS latest_timestamp
        FROM results
        WHERE metadata NOT LIKE '%prompt_version%' AND metadata NOT LIKE '%uptrain_experiment_columns%' AND timestamp > datetime('now', '-{num_days} days')
        GROUP BY project
        ORDER BY latest_timestamp DESC
        LIMIT {limit}
        """

        fpath = os.path.join(DATABASE_PATH, "uptrain-eval-results", f"{user_id}.db")
        if not os.path.exists(fpath):
            raise HTTPException(
                status_code=404, detail="No evaluations run yet for this user"
            )
        DB = get_sqlite_utils_db(fpath)

        project_runs = DB.query(query)
    except Exception:
        project_runs = []

    out = []

    for run in project_runs:
        out.append(
            {
                "project": run["project"],
                "latest_timestamp": run["latest_timestamp"],
                "run_via": "project",
            }
        )

    out.sort(reverse=True, key=lambda x: x["latest_timestamp"])
    return app_schema.ProjectsList(data=out, user_name=user_name)


@router_public.get("/get_experiments_list", response_model=app_schema.ProjectsList)
def get_experiments_list(
    num_days: int = 7,
    limit: int = 10,
    db: Session = Depends(get_db),
    user_id: str = Depends(validate_api_key_public),
):
    """Get all the experiment names associated with the user."""
    user = db.query(ModelUser).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(status_code=403, detail="Invalid user name")
    else:
        user_name = user.name

    try:
        query = f"""
        SELECT project, MAX(timestamp) AS latest_timestamp
        FROM results
        WHERE metadata LIKE '%uptrain_experiment_columns%' AND timestamp > datetime('now', '-{num_days} days')
        GROUP BY project
        ORDER BY latest_timestamp DESC
        LIMIT {limit}
        """

        fpath = os.path.join(DATABASE_PATH, "uptrain-eval-results", f"{user_id}.db")
        if not os.path.exists(fpath):
            raise HTTPException(
                status_code=404, detail="No evaluations run yet for this user"
            )
        DB = get_sqlite_utils_db(fpath)

        project_runs = DB.query(query)
    except Exception:
        project_runs = []

    out = []

    for run in project_runs:
        out.append(
            {
                "project": run["project"],
                "latest_timestamp": run["latest_timestamp"],
                "run_via": "experiment",
            }
        )

    out.sort(reverse=True, key=lambda x: x["latest_timestamp"])
    return app_schema.ProjectsList(data=out, user_name=user_name)


@router_public.get("/get_prompts_list", response_model=app_schema.ProjectsList)
def get_prompts_list(
    num_days: int = 7,
    limit: int = 10,
    db: Session = Depends(get_db),
    user_id: str = Depends(validate_api_key_public),
):
    """Get all the experiment names associated with the user."""
    user = db.query(ModelUser).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(status_code=403, detail="Invalid user name")
    else:
        user_name = user.name

    try:
        query = f"""
        SELECT project, MAX(timestamp) AS latest_timestamp
        FROM results
        WHERE metadata like '%prompt_version%' AND metadata NOT LIKE '%uptrain_experiment_columns%' AND timestamp > datetime('now', '-{num_days} days')
        GROUP BY project
        ORDER BY latest_timestamp DESC
        LIMIT {limit}
        """
        fpath = os.path.join(DATABASE_PATH, "uptrain-eval-results", f"{user_id}.db")
        if not os.path.exists(fpath):
            raise HTTPException(
                status_code=404, detail="No evaluations run yet for this user"
            )
        DB = get_sqlite_utils_db(fpath)

        prompts_runs = DB.query(query)
    except Exception:
        prompts_runs = []

    out = []

    for run in prompts_runs:
        out.append(
            {
                "project": run["project"],
                "latest_timestamp": run["latest_timestamp"],
                "run_via": "prompt",
            }
        )

    out.sort(reverse=True, key=lambda x: x["latest_timestamp"])
    return app_schema.ProjectsList(data=out, user_name=user_name)


@router_public.post("/find_common_topic")
async def find_common_topic(
    args: app_schema.TopicGenerate,
    db: Session = Depends(get_db),
    user_id: str = Depends(validate_api_key_public),
):
    """Find the common topic across the common topic."""
    items = args.items
    scores = args.scores
    dataset = list(zip(items, scores))

    refined_items = []
    for elem in dataset:
        if elem[1] is not None and elem[1] == 0.0:
            refined_items.append(elem[0])

    refined_items = refined_items[: min(50, len(refined_items))]
    data = list(
        map(
            lambda x: {"question": x, "cluster_index": 0, "cluster_index_distance": 0},
            refined_items,
        )
    )

    from uptrain.operators import TopicGenerator

    user = db.query(ModelUser).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(status_code=403, detail="Invalid user name")
    else:
        user_name = user.name

    user_headers = {"openai_api_key": user_name}

    try:
        result = (
            TopicGenerator()
            .setup(Settings(**user_headers))
            .run(pl.DataFrame(data))["output"]
        )
        return {"common_topic": result.to_dicts()[0]["topic"]}
    except Exception as exc:
        logger.exception("Error creating run")
        db.rollback()
        raise HTTPException(status_code=400, detail="Error finding common topic")


@router_public.post("/add_evaluation")
async def add_evaluation(
    model: str = Form(...),
    project_name: str = Form(...),
    dataset_name: str = Form(...),
    checks: list = Form(...),
    data_file: UploadFile = File(...),
    metadata: str = Form(...),
    user_id: str = Depends(validate_api_key_public),
    db: Session = Depends(get_db),
    fsspec_fs: t.Any = Depends(get_fsspec_fs),
):
    ## project key would be present in the eval_args.metadata

    existing_dataset = (
        db.query(ModelDataset)
        .filter_by(name=dataset_name, user_id=user_id)
        .order_by(ModelDataset.version.desc())
        .first()
    )
    if existing_dataset is not None:
        version = existing_dataset.version + 1
    else:
        version = 1
    try:
        name_w_version = os.path.join(user_id, dataset_name, f"v_{version}")
        address = os.path.join("uptrain-datasets", name_w_version)
        with fsspec_fs.open(address, "wb") as f:
            f.write(data_file.file.read())

        data_file.file.seek(0, 0)
        rows_count = len(data_file.file.readlines())
        db_item = ModelDataset(
            user_id=user_id,
            name=dataset_name,
            version=version,
            address=address,
            rows_count=rows_count,
        )
        db.add(db_item)
        db.commit()
    except Exception as exc:
        logger.exception("Error adding/updating dataset to platform")
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Error adding/updating dataset to platform"
        )
    from uptrain.operators import JsonReader
    from uptrain import Settings

    checks = eval(checks[0])
    checks_1 = []
    metadata = eval(metadata)

    for check in checks:
        if check in metadata:
            final_check = checks_mapping(check, metadata[check])
        else:
            final_check = checks_mapping(check)

        if final_check is not None:
            checks_1.append(final_check)

    settings_data = {}
    settings_data["model"] = model
    settings_data.update(metadata[model])

    try:
        from uptrain import EvalLLM

        user_client = EvalLLM(Settings(**settings_data))
        data = (
            JsonReader(
                fpath=os.path.join(DATABASE_PATH, "uptrain-datasets", name_w_version)
            )
            .setup(Settings())
            .run()["output"]
            .to_dicts()
        )
        results = user_client.evaluate(
            data=data, checks=checks_1, project_name=project_name
        )
        return {"message": f"Evaluation has been queued up"}
    except Exception as e:
        logger.exception(f"Error running the eval: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error running the evaluation: {e}"
        )


@router_public.post("/add_prompts")
async def add_prompts(
    model: str = Form(...),
    project_name: str = Form(...),
    dataset_name: str = Form(...),
    prompt: str = Form(...),
    checks: list = Form(...),
    metadata: str = Form(...),
    prompt_name: str = Form(...),
    data_file: UploadFile = File(...),
    user_id: str = Depends(validate_api_key_public),
    db: Session = Depends(get_db),
    fsspec_fs: t.Any = Depends(get_fsspec_fs),
):
    ## project key would be present in the eval_args.metadata

    user = db.query(ModelUser).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(status_code=403, detail="Invalid user name")
    else:
        user_name = user.name

    existing_dataset = (
        db.query(ModelDataset)
        .filter_by(name=dataset_name, user_id=user_id)
        .order_by(ModelDataset.version.desc())
        .first()
    )
    if existing_dataset is not None:
        version = existing_dataset.version + 1
    else:
        version = 1
    try:
        name_w_version = os.path.join(user_id, dataset_name, f"v_{version}")
        address = os.path.join("uptrain-datasets", name_w_version)
        with fsspec_fs.open(address, "wb") as f:
            f.write(data_file.file.read())

        data_file.file.seek(0, 0)
        rows_count = len(data_file.file.readlines())

        db_item = ModelDataset(
            user_id=user_id,
            name=dataset_name,
            version=version,
            address=address,
            rows_count=rows_count,
        )
        db.add(db_item)
        db.commit()
    except Exception as exc:
        logger.exception("Error adding/updating dataset to platform")
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Error adding/updating dataset to platform"
        )

    existing_prompt = (
        db.query(ModelPrompt)
        .filter_by(name=prompt_name, user_id=user_id)
        .order_by(ModelPrompt.version.desc())
        .first()
    )
    if existing_prompt is not None:
        version = existing_prompt.version + 1
    else:
        version = 1
    try:
        db_item = ModelPrompt(
            user_id=user_id, name=prompt_name, version=version, prompt=prompt
        )
        db.add(db_item)
        db.commit()
    except Exception as exc:
        logger.exception("Error adding/updating prompts to platform")
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Error adding/updating prompts to platform"
        )

    checks = eval(checks[0])
    checks_1 = []
    metadata = eval(metadata)

    for check in checks:
        if check in metadata:
            final_check = checks_mapping(check, metadata[check])
        else:
            final_check = checks_mapping(check)

        if final_check is not None:
            checks_1.append(final_check)

    settings_data = {}
    settings_data["model"] = model
    settings_data.update(metadata[model])

    from uptrain.operators import JsonReader
    from uptrain import Settings as UserSettings

    metadata = None
    metadata = {
        "project": project_name,
        "prompt": prompt,
        "prompt_name": prompt_name,
        "prompt_version": version,
        "model": model,
    }

    try:
        from uptrain import EvalLLM

        user_client = EvalLLM(Settings(**settings_data))
        data = (
            JsonReader(
                fpath=os.path.join(DATABASE_PATH, "uptrain-datasets", name_w_version)
            )
            .setup(UserSettings())
            .run()["output"]
            .to_dicts()
        )
        results = user_client.evaluate_prompts(
            project_name=project_name,
            data=data,
            checks=checks_1,
            prompt=prompt,
            metadata=metadata,
        )
        return {"message": f"Evaluation has been queued up"}
    except Exception as e:
        logger.exception(f"Error running the eval: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error running the evaluation: {e}"
        )


# -----------------------------------------------------------
# FastAPI app
# -----------------------------------------------------------

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router_public, prefix="/api/public", tags=["public"])
app.include_router(router_internal, prefix="/api/internal", tags=["internal"])

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=4300, workers=3)
