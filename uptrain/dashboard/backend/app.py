"""Uptrain server to receive evaluation requests from clients, and 
schedule them on execute. 
 
NOTE: Make sure all public api methods make use of `user_name` to only 
work with rows specific to the user.
"""

from __future__ import annotations
from contextlib import contextmanager
import datetime as dt
import json
import io
import os
import typing as t
import copy 
import random
import uvicorn
import polars as pl
import sys

from uptrain.operators import JsonReader, JsonWriter

from uptrain import Settings as UserSettings
from uptrain import EvalLLM

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

def get_uuid():
    import uuid
    return str(uuid.uuid4().hex)

from loguru import logger
from sqlalchemy.orm import Session

from uptrain.utilities.db import create_database, ModelUser, ModelPrompt, ModelProject, ModelProjectDataset, ModelProjectRun
from uptrain.utilities.utils import (
    _get_fsspec_filesystem,
    checks_mapping,
    create_dirs,
)

from uptrain.utilities import app_schema


def _row_to_dict(row):
    return {k: v for k, v in row.__dict__.items() if not k.startswith("_")}

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


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

# # -----------------------------------------------------------
# # Internal API
# # -----------------------------------------------------------


# @router_internal.post("/user")
# def add_user(user: app_schema.UserCreate, db: Session = Depends(get_db)):
#     """Add a new user."""
#     name = user.name
#     try:
#         db_user = _create_user(db, name)
#         return db_user
#     except Exception as exc:
#         logger.exception(exc)
#         raise HTTPException(status_code=400, detail=f"Error creating user: {name}")


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

@router_public.get("/get_data", response_model=app_schema.ProjectData)
def get_data(
    evaluation_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(validate_api_key_public),
):
    """Get all the data for a particular evaluation for the given user.
    """
    user = db.query(ModelUser).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(status_code=403, detail="Invalid user name")
    else:
        user_name = user.name

    project_run = db.query(ModelProjectRun).filter_by(id=evaluation_id).first()

    address = project_run.address
    exp_column = project_run.exp_column
    run_type = project_run.run_type
    created_at = project_run.created_at
    checks = project_run.checks

    data = JsonReader(fpath = address).setup(UserSettings()).run()['output'].to_dicts()

    if run_type == "evaluation" or run_type == "experiment" or run_type == "prompt":
        scores = [col[6:] for col in data[0].keys() if (col.startswith("score_") and 'confidence' not in col)]
        if run_type == "evaluation" or run_type == "prompt":
            return app_schema.ProjectData(data=[data, created_at, scores, checks], id=evaluation_id)
        else:
            plot_data = {}
            exp_data = pl.DataFrame(data)
            for col in scores:
                col_name = 'score_' + col
                plot_data.update({col : exp_data.group_by([exp_column], maintain_order=True).agg(pl.col(col_name)).to_dicts()})

            columns = exp_data.columns
            columns.remove('question')
            display_data = exp_data.group_by(["question"], maintain_order=True).agg(pl.col(col) for col in columns).to_dicts()
            unqiue_values  = list(set(exp_data[exp_column].to_list()))
            return app_schema.ProjectData(data = [display_data, created_at, scores, unqiue_values, exp_column, plot_data, checks], id = evaluation_id)



def _save_log_and_eval(
        project_name: str, 
        evaluation_name: str, 
        metadata: dict,
        user_id: str, 
        source_data: list[dict],
        sink_data: list[dict],
        checks: list[dict], 
        db: Session,
        exp_column: t.Optional[str] = None
    ):
    existing_project = (
        db.query(ModelProject)
        .filter_by(name=project_name, user_id=user_id)
        .first()
    )
    if existing_project is not None:
        project_id = existing_project.id
    else:
        project_id = get_uuid()
    

    if "dataset_id" not in metadata:
        ######    
        if "dataset_name" in metadata:
            dataset_name = metadata["dataset_name"]
        else:
            dataset_name = project_name + "__" + evaluation_name
        dataset_id = get_uuid()

        existing_dataset = (
            db.query(ModelProjectDataset)
            .filter_by(name=dataset_name, user_id=user_id)
            .order_by(ModelProjectDataset.version.desc())
            .first()
        )
        if existing_dataset is not None:
            version = existing_dataset.version + 1
        else:
            version = 1
        #####    
        try:
            name_w_version = os.path.join(user_id, dataset_name)
            address = os.path.join(DATABASE_PATH, "uptrain-datasets", name_w_version)
            os.makedirs(address, exist_ok=True)
            address = os.path.join(address, f"v_{version}")
            JsonWriter(fpath=address).setup(UserSettings()).run(pl.DataFrame(source_data))
            rows_count = len(source_data)
            db_item = ModelProjectDataset(
                id=dataset_id,
                project_id=project_id,
                user_id=user_id,
                name=dataset_name,
                version=version,
                address=address,
                rows_count=rows_count
            )
            db.add(db_item)
            db.commit()
        except Exception as exc:
            logger.exception("Error adding/updating dataset to platform")
            db.rollback()
            raise HTTPException(
                status_code=400, detail="Error adding/updating dataset to platform"
            )
    else:
        existing_dataset = (
            db.query(ModelProjectDataset)
            .filter_by(id=metadata["dataset_id"], user_id=user_id)
            .order_by(ModelProjectDataset.version.desc())
            .first()
        )
        dataset_id = existing_dataset.id

    for check in checks:
        for key, value in check.copy().items():
            ## to remove scenario description
            if value is None:
                del check[key]
    try:
        if existing_project is None:
            db_item = ModelProject(
                id=project_id,
                name=project_name,
                user_id=user_id,
                dataset_id=dataset_id,
                checks=json.dumps({"checks": checks})
            )
            db.add(db_item)
            db.commit()
    except Exception as exc:
        logger.exception("Error adding project to platform")
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Error adding project to platform"
        )       
    
    evaluation_id = get_uuid()

    name_w_version = os.path.join("uptrain-eval-results", evaluation_id)
    address = os.path.join(DATABASE_PATH, name_w_version)

    JsonWriter(fpath=address).setup(UserSettings()).run(pl.DataFrame(sink_data))
    run_type = "evaluation"
    if exp_column is not None:
        run_type = "experiment"
    elif "prompt_id" in metadata:
        run_type = "prompt"
    add_project_run(
        app_schema.EvalCreate(
            evaluation_id=evaluation_id, 
            evaluation_name=evaluation_name,
            dataset_id=dataset_id,
            project_id=project_id,
            address=address,
            user_id=user_id,
            run_type=run_type,
            checks={"checks": checks},
            exp_column=exp_column,
            prompt_id = metadata.get("prompt_id", None)
        ),
        db
    )
    return 

def _create_evaluation(db: Session, evaluation_id: str, evaluation_name: str, address: str,  project_id: str, dataset_id: str, user_id: str, run_type: str, checks: dict, exp_column: str=None, prompt_id: str=None):
    """Create a new evaluation."""
    if exp_column is not None:
        db_eval = ModelProjectRun(id=evaluation_id, name=evaluation_name, address=address, project_id=project_id, dataset_id=dataset_id, user_id=user_id, run_type=run_type, exp_column=exp_column, checks=checks)
    else:
        if prompt_id is not None:
            db_eval = ModelProjectRun(id=evaluation_id, name=evaluation_name, address=address, project_id=project_id, dataset_id=dataset_id, user_id=user_id, run_type=run_type, prompt_id=prompt_id, checks=checks)
        else:
            db_eval = ModelProjectRun(id=evaluation_id, name=evaluation_name, address=address, project_id=project_id, dataset_id=dataset_id, user_id=user_id, run_type=run_type, checks=checks)
    try:
        db.add(db_eval)
        db.commit()
        return db_eval
    except Exception as exc:
        db.rollback()
        raise exc
    

@router_internal.post("/evaluation")
def add_project_run(
    evaluation: app_schema.EvalCreate,
    db: Session = Depends(get_db)
):
    try:
        db_eval = _create_evaluation(
            db, 
            evaluation.evaluation_id, 
            evaluation.evaluation_name, 
            evaluation.address, 
            evaluation.project_id, 
            evaluation.dataset_id, 
            evaluation.user_id, 
            evaluation.run_type,
            evaluation.checks,
            evaluation.exp_column,
            evaluation.prompt_id
        )
        return db_eval
    except Exception as exc:
        logger.exception(exc)
        raise HTTPException(status_code=400, detail=f"Error creating the evaluation: {evaluation.evaluation_name}")
    
@router_public.post("/add_project_data")
async def add_project_data(
    eval_args: app_schema.EvaluateV2,
    user_id: str = Depends(validate_api_key_public),
    db: Session = Depends(get_db),
):

    project_name = eval_args.project
    evaluation_name = eval_args.evaluation
    sink_data = eval_args.sink_data
    exp_column = eval_args.exp_column
    metadata = eval_args.metadata

    _save_log_and_eval(
                project_name=project_name, 
                evaluation_name=evaluation_name, 
                metadata = metadata,
                user_id=user_id,
                source_data=eval_args.data,
                sink_data=sink_data,
                checks=eval_args.checks,
                db=db,
                exp_column=exp_column
            )
    return


@router_public.get("/projects", response_model=list[app_schema.Project])
def list_projects(
    num: int = 10,
    num_days: int = 7,
    db: Session = Depends(get_db),
    user_id: str = Depends(validate_api_key_public),
):
    """Get the last N runs for the user (non-scheduled). Optionally filter by status."""
    query = (
        db.query(ModelProject)
        .filter(ModelProject.user_id == user_id)
    )
    
    projects = query.order_by(ModelProject.created_at.desc()).limit(num).all()

    # Convert to list of dicts for easier serialization
    results = []
    ### This will include evaluations, experiments and prompts run. 
    for project in projects:
        results.append(
            app_schema.Project(
                project_type="project",
                project_id=project.id,
                created_at=project.created_at,
                project_name=project.name,
                dataset_id=project.dataset_id,
                checks=eval(project.checks)
            )
        )
    return results


@router_public.get("/project_runs", response_model=list[app_schema.ProjectRun])
def list_project_runs(
    project_id: str,
    num_days: int = 7,
    num: int = 10,
    db: Session = Depends(get_db),
    user_id: str = Depends(validate_api_key_public),
):
    """Get the last N runs for the user (non-scheduled). Optionally filter by status."""
    query = (
        db.query(ModelProjectRun)
        .filter(ModelProjectRun.user_id == user_id, ModelProjectRun.project_id == project_id)
    )

    project_runs = query.order_by(ModelProjectRun.created_at.desc()).limit(num).all()

    # Convert to list of dicts for easier serialization
    results = []
    for run in project_runs:
        results.append(
            app_schema.ProjectRun(
                evaluation_id=run.id,
                evaluation_name=run.name,
                project_id=run.project_id,
                created_at=run.created_at,
                dataset_id=run.dataset_id,
                run_type=run.run_type,
                exp_column=run.exp_column
            )
        )

    return results


@router_public.get("/prompt_runs", response_model=list[app_schema.PromptRun])
def prompt_runs(
    project_id: str,
    num: int = 10,
    db: Session = Depends(get_db),
    user_id: str = Depends(validate_api_key_public),
):
    """Get the last N runs for the user (non-scheduled). Optionally filter by status."""
    query = (
        db.query(ModelPrompt)
        .filter(ModelPrompt.user_id == user_id, ModelPrompt.project_id == project_id)
    )

    prompt_runs = query.order_by(ModelPrompt.created_at.asc()).limit(num).all()

    results = []
    prompts = []
    for run in prompt_runs:
        prompt_id = run.id
        prompt_name = run.name
        prompt_version = run.version
        prompt = run.prompt
        prompt_dict = {'prompt_id': prompt_id, 'prompt_name': prompt_name, 'prompt_version': prompt_version, 'prompt': prompt}
        query_prompt_data = db.query(ModelProjectRun).filter(ModelProjectRun.prompt_id == prompt_id, ModelProjectRun.user_id == user_id).first()

        if query_prompt_data is None: #or not len(list(query_prompt_data)):
            continue
        prompt_run = query_prompt_data
        
        evaluation_id = prompt_run.id 
        prompt_dict['evaluation_id'] = evaluation_id
        prompt_dict['created_at'] = prompt_run.created_at
        prompt_dict['dataset_id'] = prompt_run.dataset_id
        address = prompt_run.address
        data = JsonReader(fpath = address).setup(UserSettings()).run()['output'].to_dicts()
        data_df = pl.DataFrame(data)
        scores = [col for col in data[0].keys() if (col.startswith("score_") and "confidence" not in col)]
        scores_dict = {}
        mean_values = data_df.mean().to_dicts()[0]
        for score in scores:
            scores_dict[score] = round(mean_values[score], 2)
        prompt_dict['scores'] = scores_dict
        prompts.append(copy.deepcopy(prompt_dict))
     
    for run in prompts:
        results.append(
            app_schema.PromptRun(
                evaluation_id=run['evaluation_id'],
                prompt_id=run['prompt_id'],
                prompt_name=run['prompt_name'],
                prompt_version=run['prompt_version'],
                prompt=run['prompt'],
                created_at=run['created_at'],
                dataset_id=run['dataset_id'],
                scores=run['scores']
            )
        )
    return results


@router_public.get("/compare_prompt", response_model=app_schema.ProjectData)
def compare_prompt(
    evaluation_id_1: str,
    evaluation_id_2: str,
    version_1: t.Union[str, int],
    version_2: t.Union[str, int],
    db: Session = Depends(get_db),
    user_id: str = Depends(validate_api_key_public),
):
    """Get all the data for a particular evaluation for the given user.
    """
    user = db.query(ModelUser).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(status_code=403, detail="Invalid user name")
    else:
        user_name = user.name

    project_run_1 = db.query(ModelProjectRun).filter_by(id=evaluation_id_1).first()
    project_run_2 = db.query(ModelProjectRun).filter_by(id=evaluation_id_2).first()

    address_1 = project_run_1.address
    address_2 = project_run_2.address
    created_at_1 = project_run_1.created_at
    created_at_2 = project_run_2.created_at

    
    data_1 = JsonReader(fpath = address_1).setup(UserSettings()).run()['output'].with_columns(
        experiment_column = pl.lit(str(version_1))
    ).to_dicts()
    data_2 = JsonReader(fpath = address_2).setup(UserSettings()).run()['output'].with_columns(
        experiment_column = pl.lit(str(version_2))
    ).to_dicts()

    combined_data = pl.concat([pl.DataFrame(data_1), pl.DataFrame(data_2)], how="diagonal").to_dicts()
    
    scores_1 = [col[6:] for col in data_1[0].keys() if (col.startswith("score_") and 'confidence' not in col)]
    scores_2 = [col[6:] for col in data_2[0].keys() if (col.startswith("score_") and 'confidence' not in col)]
    common_scores = intersection(scores_1, scores_2)

    plot_data = {}
    exp_column = 'experiment_column'
    exp_data = pl.DataFrame(combined_data)
    for col in common_scores:
        col_name = 'score_' + col
        plot_data.update({col : exp_data.group_by([exp_column], maintain_order=True).agg(pl.col(col_name)).to_dicts()})

    columns = exp_data.columns
    columns.remove('question')
    display_data = exp_data.group_by(["question"], maintain_order=True).agg(pl.col(col) for col in columns).to_dicts()
    unqiue_values  = list(set(exp_data[exp_column].to_list()))
    return app_schema.ProjectData(data = [display_data, created_at_1, common_scores, unqiue_values, exp_column, plot_data], id = evaluation_id_1)


@router_public.get("/project_datasets", response_model=list[app_schema.ProjectDataset])
def list_project_datasets(
    project_id: str, 
    db: Session = Depends(get_db),
    user_id: str = Depends(validate_api_key_public),
):
    datasets = (
        db.query(ModelProjectDataset)
        .filter_by(user_id=user_id, project_id=project_id)
        .all()
    )
    return [
        app_schema.ProjectDataset(name=db_item.name, version=db_item.version, id=db_item.id)
        for db_item in datasets
    ]


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
            .setup(UserSettings(**user_headers))
            .run(pl.DataFrame(data))["output"]
        )
        return {"common_topic": result.to_dicts()[0]["topic"]}
    except Exception as exc:
        logger.exception("Error creating run")
        db.rollback()
        raise HTTPException(status_code=400, detail="Error finding common topic")


@router_public.post("/create_project")
async def create_project(
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

    existing_project = (
        db.query(ModelProject)
        .filter_by(name=project_name, user_id=user_id)
        .first()
    )
    if existing_project is not None:
        raise HTTPException(
            status_code=400, detail="cannot create a project with the same name."
        )
    
    evaluation_name = "default_run"
    version = str(random.random()).split('.')[-1][:2]
    name_w_version = os.path.join(user_id, dataset_name, f"v_{version}")
    address = os.path.join("temp-datasets", name_w_version)
    with fsspec_fs.open(address, "wb") as f:
        f.write(data_file.file.read())

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
    settings_data["uptrain_local_url"] = os.environ["UPTRAIN_LOCAL_URL"]
    settings_data.update(metadata[model])

    if "exp_column" in metadata:
        exp_column = metadata["exp_column"]
    else:
        exp_column = None
    
    try:
        user_client = EvalLLM(UserSettings(**settings_data))
        data = (
            JsonReader(
                fpath=os.path.join(DATABASE_PATH, "temp-datasets", name_w_version)
            )
            .setup(UserSettings())
            .run()["output"]
            .to_dicts()
        )
        metadata = {'dataset_name': dataset_name}
        if exp_column is None:
            results = user_client.evaluate(
                data=data, checks=checks_1, project_name=project_name, evaluation_name=evaluation_name, metadata=metadata
            )
        else:
            results = user_client.evaluate_experiments(
                data=data, checks=checks_1, project_name=project_name, evaluation_name=evaluation_name, exp_columns=[exp_column], metadata=metadata
            )
        return {"message": f"Evaluation has been queued up"}
    except Exception as e:
        logger.exception(f"Error running the eval: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error running the evaluation: {e}"
        )



@router_public.post("/new_run")
async def new_run(
    model: str = Form(...),
    dataset_name: str = Form(...),
    evaluation_name: str = Form(...),
    checks: list = Form(...),
    project_id: str = Form(...),
    data_file: UploadFile = File(...),
    metadata: str = Form(...),
    user_id: str = Depends(validate_api_key_public),
    db: Session = Depends(get_db),
    fsspec_fs: t.Any = Depends(get_fsspec_fs),
):
    ## project key would be present in the eval_args.metadata

    existing_project = (
        db.query(ModelProject)
        .filter_by(id=project_id)
        .first()
    )
    
    checks = eval(checks[0])
    checks_1 = []
    metadata = eval(metadata)

    version = str(random.random()).split('.')[-1][:2]
    name_w_version = os.path.join(user_id, dataset_name, f"v_{version}")
    address = os.path.join("temp-datasets", name_w_version)
    with fsspec_fs.open(address, "wb") as f:
        f.write(data_file.file.read())

    for check in checks:
        if check in metadata:
            final_check = checks_mapping(check, metadata[check])
        else:
            final_check = checks_mapping(check)

        if final_check is not None:
            checks_1.append(final_check)

    settings_data = {}
    settings_data["model"] = model
    settings_data["uptrain_local_url"] = os.environ["UPTRAIN_LOCAL_URL"]
    settings_data.update(metadata[model])

    if "exp_column" in metadata:
        exp_column = metadata["exp_column"]
    else:
        exp_column = None

    try:
        user_client = EvalLLM(UserSettings(**settings_data))
        data = (
            JsonReader(
                fpath=os.path.join(DATABASE_PATH, "temp-datasets", name_w_version)
            )
            .setup(UserSettings())
            .run()["output"]
            .to_dicts()
        )
        metadata = {'dataset_name': dataset_name}
        if exp_column is None:
            results = user_client.evaluate(
                data=data, checks=checks_1, project_name=existing_project.name, evaluation_name=evaluation_name, metadata=metadata
            )
        else:
            results = user_client.evaluate_experiments(
                data=data, checks=checks_1, project_name=existing_project.name, evaluation_name=evaluation_name, exp_columns=[exp_column], metadata=metadata
            )
        return {"message": f"Evaluation has been queued up"}
    except Exception as e:
        logger.exception(f"Error running the eval: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error running the evaluation: {e}"
        )
    


@router_public.post("/add_default_run")
async def add_default_run(
    eval_args: app_schema.DefaultRun,
    user_id: str = Depends(validate_api_key_public),
    db: Session = Depends(get_db)
):
    ## project key would be present in the eval_args.metadata
    dataset_id = eval_args.dataset_id
    project_id = eval_args.project_id

    existing_project = (
        db.query(ModelProject)
        .filter_by(id=project_id)
        .first()
    )


    existing_dataset = (
        db.query(ModelProjectDataset)
        .filter_by(id=dataset_id, user_id=user_id)
        .order_by(ModelProjectDataset.version.desc())
        .first()
    )

    if existing_dataset is None:
        raise HTTPException(status_code=500, detail="Invalid dataset provided")

    dataset_name = existing_dataset.name
    version = existing_dataset.version

    name_w_version = os.path.join(user_id, dataset_name, f"v_{version}")
    address = os.path.join('uptrain-datasets', name_w_version)
    
    checks = eval_args.checks
    checks_1 = []
    metadata = eval_args.metadata
            
    for check in checks:
        if check in metadata:
            final_check = checks_mapping(check, metadata[check])
        else:
            final_check = checks_mapping(check)
        if final_check is not None:
            checks_1.append(final_check)

    settings_data = {}
    settings_data["model"] = eval_args.model
    settings_data["uptrain_local_url"] = os.environ["UPTRAIN_LOCAL_URL"]
    settings_data.update(metadata[eval_args.model])

    if "exp_column" in metadata:
        exp_column = metadata["exp_column"]
    else:
        exp_column = None

    try:
        user_client = EvalLLM(UserSettings(**settings_data))
        data = (
            JsonReader(
                fpath=os.path.join(DATABASE_PATH, address)
            )
            .setup(UserSettings())
            .run()["output"]
            .to_dicts()
        )
        metadata = {'dataset_name': dataset_name, 'dataset_id': dataset_id}
        if exp_column is None:
            results = user_client.evaluate(
                data=data, checks=checks_1, project_name=existing_project.name, evaluation_name=eval_args.evaluation_name, metadata=metadata
            )
        else:
            results = user_client.evaluate_experiments(
                data=data, checks=checks_1, project_name=existing_project.name, evaluation_name=eval_args.evaluation_name, exp_columns=[exp_column], metadata=metadata
            )
        return {"message": f"Evaluation has been queued up"}
    except Exception as e:
        logger.exception(f"Error running the eval: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error running the evaluation: {e}"
        )


@router_public.post("/add_prompts")
async def add_prompts(  
    project_id: str = Form(...),
    model: str = Form(...),
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

    # user = db.query(ModelUser).filter_by(id=user_id).first()
    # if user is None:
    #     raise HTTPException(status_code=403, detail="Invalid user name")
    # else:
    #     user_name = user.name

    existing_project = (
        db.query(ModelProject)
        .filter_by(id=project_id)
        .first()
    )
    
    checks = eval(checks[0])
    checks_1 = []
    metadata = eval(metadata)

    version = str(random.random()).split('.')[-1][:2]
    name_w_version = os.path.join(user_id, dataset_name, f"v_{version}")
    address = os.path.join("temp-datasets", name_w_version)
    with fsspec_fs.open(address, "wb") as f:
        f.write(data_file.file.read())

    for check in checks:
        if check in metadata:
            final_check = checks_mapping(check, metadata[check])
        else:
            final_check = checks_mapping(check)

        if final_check is not None:
            checks_1.append(final_check)

    settings_data = {}
    settings_data["model"] = model
    settings_data["uptrain_local_url"] = os.environ["UPTRAIN_LOCAL_URL"]
    settings_data.update(metadata[model])
    prompt_id = get_uuid()

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
            id=prompt_id, user_id=user_id, name=prompt_name, version=version, prompt=prompt, project_id=project_id
        )
        db.add(db_item)
        db.commit()
    except Exception as exc:
        logger.exception("Error adding/updating prompts to platform")
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Error adding/updating prompts to platform"
        )

    metadata = {
        "dataset_name": dataset_name,
        "prompt_id": prompt_id,
        "model": model,
    }

    try:
        user_client = EvalLLM(UserSettings(**settings_data))
        data = (
            JsonReader(
                fpath=os.path.join(DATABASE_PATH, "temp-datasets", name_w_version)
            )
            .setup(UserSettings())
            .run()["output"]
            .to_dicts()
        )
        results = user_client.evaluate_prompts(
            project_name=existing_project.name,
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




@router_public.post("/add_default_prompt")
async def add_default_prompt(
    eval_args: app_schema.DefaultPrompt,
    user_id: str = Depends(validate_api_key_public),
    db: Session = Depends(get_db)
):
    ## project key would be present in the eval_args.metadata
    prompt_id = get_uuid()

    dataset_id = eval_args.dataset_id
    project_id = eval_args.project_id

    prompt_name = eval_args.prompt_name
    prompt = eval_args.prompt

    existing_project = (
        db.query(ModelProject)
        .filter_by(id=project_id)
        .first()
    )


    existing_dataset = (
        db.query(ModelProjectDataset)
        .filter_by(id=dataset_id, user_id=user_id)
        .order_by(ModelProjectDataset.version.desc())
        .first()
    )

    if existing_dataset is None:
        raise HTTPException(status_code=500, detail="Invalid dataset provided")

    dataset_name = existing_dataset.name
    version = existing_dataset.version

    name_w_version = os.path.join(user_id, dataset_name, f"v_{version}")
    address = os.path.join('uptrain-datasets', name_w_version)
    
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
            id=prompt_id,
            project_id=project_id,
            user_id=user_id,
            name=prompt_name,
            version=version,
            prompt=prompt
        )
        db.add(db_item)
        db.commit()
    except Exception as exc:
        logger.exception("Error adding/updating prompts to platform")
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Error adding/updating prompts to platform"
        )
    
    checks = eval_args.checks
    checks_1 = []
    metadata = eval_args.metadata
            
    for check in checks:
        if check in metadata:
            final_check = checks_mapping(check, metadata[check])
        else:
            final_check = checks_mapping(check)
        if final_check is not None:
            checks_1.append(final_check)

    settings_data = {}
    settings_data["model"] = eval_args.model
    settings_data["uptrain_local_url"] = os.environ["UPTRAIN_LOCAL_URL"]
    settings_data.update(metadata[eval_args.model])


    metadata = {
        "dataset_id": dataset_id,
        "prompt_id": prompt_id,
        "model": eval_args.model,
    }

    data = JsonReader(fpath=os.path.join(DATABASE_PATH, address)).setup(UserSettings()).run()['output'].to_dicts()
    
    try:
        user_client = EvalLLM(UserSettings(**settings_data))
        results = user_client.evaluate_prompts(
            project_name=existing_project.name,
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
