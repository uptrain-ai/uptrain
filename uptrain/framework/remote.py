"""
This module implements a simple client that can be used to schedule unit-tests/evaluations 
on the UpTrain server. 
"""

import enum
import typing as t

from loguru import logger
import httpx
import polars as pl
import pydantic

from uptrain.framework.checks import CheckSet, ExperimentArgs
from uptrain.framework.base import Settings
from uptrain.utilities import to_py_types


class DataSchema(pydantic.BaseModel):
    id_: str = "id"
    question: str = "question"
    response: str = "response"
    context: str = "context"
    ground_truth: str = "ground_truth"


class Evals(enum.Enum):
    CONTEXT_RELEVANCE = "context_relevance"
    FACTUAL_ACCURACY = "factual_accuracy"
    RESPONSE_RELEVANCE = "response_relevance"


def raise_or_return(response: httpx.Response):
    if not response.is_success:
        logger.error(response.text)
        response.raise_for_status()
    else:
        return response.json()


class APIClient:
    base_url: str
    client: httpx.Client

    def __init__(self, settings: Settings) -> None:
        server_url = settings.check_and_get("uptrain_server_url")
        api_key = settings.check_and_get("uptrain_access_token")
        self.base_url = server_url.rstrip("/") + "/api/public"
        self.client = httpx.Client(
            headers={"uptrain-access-token": api_key},
            timeout=httpx.Timeout(50, connect=5),
        )

    def check_auth(self):
        """Ping the server to check if the client is authenticated."""
        url = f"{self.base_url}/auth"
        try:
            response = self.client.get(url)
            return raise_or_return(response)
        except httpx.ConnectError as e:
            raise RuntimeError(
                f"Failed to connect to the Uptrain server at {self.base_url}"
            ) from e

    def add_dataset(self, name: str, fpath: str):
        url = f"{self.base_url}/dataset"
        with open(fpath, "rb") as file:
            files = {"data_file": (name, file, "application/octet-stream")}
            response = self.client.post(url, data={"name": name}, files=files)
        return raise_or_return(response)

    def get_dataset(self, name: str, version: t.Optional[int] = None):
        url = f"{self.base_url}/dataset"
        params: dict = {"name": name}
        if version is not None:
            params["version"] = version
        response = self.client.get(url, params=params)
        return raise_or_return(response)

    def list_datasets(self, skip: int = 0, limit: int = 100):
        url = f"{self.base_url}/datasets"
        params = {"skip": skip, "limit": limit}
        response = self.client.get(url, params=params)
        return raise_or_return(response)

    def download_dataset(
        self, name: str, fpath: str, version: t.Optional[int] = None
    ) -> None:
        """
        Download a dataset from the server.

        Args:
            name: name of the dataset to download
            fpath: path to save the dataset to
            version: version of the dataset to download. If None, the latest version is downloaded.
        """
        url = f"{self.base_url}/dataset/{name}/download"
        params: dict = {}
        if version is not None:
            params["version"] = version
        response = self.client.get(url, params=params)
        if not response.is_success:
            logger.error(response.text)
            response.raise_for_status()
        else:
            with open(fpath, "wb") as download_file:
                for chunk in response.iter_bytes():
                    download_file.write(chunk)

    def add_checkset(self, name: str, checkset: CheckSet, settings: Settings):
        url = f"{self.base_url}/checkset"
        response = self.client.post(
            url,
            json={"name": name, "config": checkset.dict(), "settings": settings.dict()},
        )
        return raise_or_return(response)

    def get_checkset(self, name: str, version: t.Optional[int] = None):
        url = f"{self.base_url}/checkset"
        params: dict = {"name": name}
        if version is not None:
            params["version"] = version
        response = self.client.get(url, params=params)
        return raise_or_return(response)

    def list_checksets(self, skip: int = 0, limit: int = 10):
        url = f"{self.base_url}/checksets"
        params = {"skip": skip, "limit": limit}
        response = self.client.get(url, params=params)
        return raise_or_return(response)

    def add_experiment(
        self,
        name: str,
        checkset: CheckSet,
        experiment_args: ExperimentArgs,
        settings: Settings,
    ):
        preprocessors = experiment_args._get_preprocessors()
        modified_checks = experiment_args._modify_checks(checkset.checks)
        modified_checkset = CheckSet(
            source=checkset.source, checks=modified_checks, preprocessors=preprocessors
        )
        url = f"{self.base_url}/checkset"
        response = self.client.post(
            url,
            json={
                "name": name,
                "config": modified_checkset.dict(),
                "settings": settings.dict(),
            },
        )
        return raise_or_return(response)

    def add_run(self, dataset: str, checkset: str):
        """Schedules an evaluation on the server. Specify the dataset and checkset to use.

        Args:
            dataset: name of the dataset to use
            checkset: name of the checkset to use

        Returns:
            run: information about the run along with a unique identifier.
        """
        url = f"{self.base_url}/run"
        response = self.client.post(
            url, json={"dataset": dataset, "checkset": checkset}
        )
        return raise_or_return(response)

    def get_run(self, run_id: str):
        """Get the status of a run.

        Args:
            run_id: unique identifier for the run.

        Returns:
            run: information about the run along with a unique identifier.
        """
        url = f"{self.base_url}/run/{run_id}"
        response = self.client.get(url)
        return raise_or_return(response)

    def download_run_result(self, run_id: str, check_name: str, fpath: str) -> None:
        """Get the results of a run.

        Args:
            run_id: unique identifier for the run.
            check_name: name of the check to get results for.
            fpath: path to save the results to.
        """
        url = f"{self.base_url}/run/{run_id}/results"
        params: dict = {"check_name": check_name}
        with self.client.stream("GET", url, params=params) as response:
            if not response.is_success:
                logger.error(response.text)
                response.raise_for_status()
            else:
                with open(fpath, "wb") as download_file:
                    for chunk in response.iter_bytes():
                        download_file.write(chunk)

    def list_runs(self, num: int = 10, only_completed: bool = False):
        """List all the runs on the server.

        - filter by scheduled/completed/in-process?
        """
        url = f"{self.base_url}/runs"
        params: dict = {"num": num}
        if only_completed:
            params["status"] = "completed"
        response = self.client.get(url, params=params)
        return raise_or_return(response)

    def add_daily_schedule(self, checkset: str, start_on: str):
        """Schedules a periodic evaluation on the server. Specify the checkset to run against it.

        Args:
            checkset: name of the checkset to use
            start_on: date to start the schedule on

        Returns:
            run: information about the schedule along with a unique identifier.
        """
        url = f"{self.base_url}/schedule"
        response = self.client.post(
            url, json={"checkset": checkset, "start_on": start_on}
        )
        return raise_or_return(response)

    def get_schedule(self, schedule_id: str):
        """Get the status of a schedule.

        Args:
            schedule_id: unique identifier for the schedule.

        Returns:
            run: information about the schedule along with a unique identifier.
        """
        url = f"{self.base_url}/schedule/{schedule_id}"
        response = self.client.get(url)
        return raise_or_return(response)

    def remove_schedule(self, schedule_id: str):
        """Remove a schedule.

        Args:
            schedule_id: unique identifier for the schedule.

        Returns:
            run: information about the schedule along with a unique identifier.
        """
        url = f"{self.base_url}/schedule/{schedule_id}"
        response = self.client.delete(url)
        return raise_or_return(response)

    def list_schedules(self, num: int = 10, active_only: bool = True):
        """List all the schedules on the server."""
        url = f"{self.base_url}/schedules"
        params: dict = {"num": num, "active_only": active_only}
        response = self.client.get(url, params=params)
        return raise_or_return(response)

    def rerun_schedule(
        self, schedule_id: str, start_on: str, end_on: t.Optional[str] = None
    ):
        """Rerun a schedule.
        - New checks added to the checkset are run for all dates
        - Existing checks are run only on the failed rows.

        Args:
            schedule_id: unique identifier for the run.
            start_on: date to start the reruns on
            end_on: date to end the reruns on

        Returns:
            run: information about the schedule along with a unique identifier.
        """
        url = f"{self.base_url}/schedule/{schedule_id}/rerun"
        params = {"start_on": start_on}
        if end_on is not None:
            params["end_on"] = end_on
        response = self.client.put(url, params=params)
        return raise_or_return(response)

    def evaluate(
        self,
        eval_name: str,
        full_dataset: t.Union[list[dict], pl.DataFrame],
        params: dict | None = None,
    ):
        """Run an evaluation on the server.

        NOTE: Internal use only. Use regular uptrain operators to run evaluations,
        """
        url = f"{self.base_url}/evaluate"
        if isinstance(full_dataset, pl.DataFrame):
            full_dataset = full_dataset.to_dicts()

        # send in chunks of 50, so the connection doesn't time out waiting for the server
        results = []
        NUM_TRIES = 3
        for i in range(0, len(full_dataset), 10):
            response_json = None
            for try_num in range(NUM_TRIES):
                try:
                    logger.info(
                        f"Sending evaluation request for rows {i} to <{i+10} to the Uptrain server"
                    )
                    response = self.client.post(
                        url,
                        json={
                            "eval_name": eval_name,
                            "dataset": full_dataset[i : i + 10],
                            "params": params if params is not None else {},
                        },
                    )
                    response_json = raise_or_return(response)
                    break
                except Exception as e:
                    logger.info("Retrying evaluation request")
                    if try_num == NUM_TRIES - 1:
                        logger.error(f"Evaluation failed with error: {e}")
                        raise e

            if response_json is not None:
                results.extend(response_json)

        return results

    def log_and_evaluate(
        self,
        project_name: str,
        data: t.Union[list[dict], pl.DataFrame],
        checks: list[t.Union[str, Evals]],
        schema: t.Union[DataSchema, dict[str, str], None] = None,
        metadata: t.Optional[dict[str, t.Any]] = None,
    ):
        """Run an evaluation on the server and log the results.
        NOTE: This api is a bit different than the regular `evaluate` call.

        Args:
            project_name: Name of the project to evaluate on.
            data: Data to evaluate on. Either a Pandas DataFrame or a list of dicts.
            checks: List of checks to evaluate on.
            schema: Schema of the data. Only required if the data attributes aren't typical (question, response, context).
            metadata: Attributes to attach to this dataset. Useful for filtering and grouping in the UI.

        Returns:
            results: List of dictionaries with each data point and corresponding evaluation results.
        """
        url = f"{self.base_url}/log_and_evaluate"

        if isinstance(data, pl.DataFrame):
            data = data.to_dicts()

        if schema is None:
            schema = DataSchema()
        elif isinstance(schema, dict):
            schema = DataSchema(**schema)

        if metadata is None:
            metadata = {}

        metrics = [Evals(m) if isinstance(m, str) else m for m in metrics]
        for m in metrics:
            assert isinstance(m, (Evals, ParametricEval))

        req_attrs, ser_metrics = set(), []
        for m in metrics:
            if m in [Evals.FACTUAL_ACCURACY, Evals.RESPONSE_COMPLETENESS_WRT_CONTEXT]:
                req_attrs.update([schema.question, schema.context, schema.response])
            elif m in [Evals.RESPONSE_RELEVANCE, Evals.RESPONSE_COMPLETENESS]:
                req_attrs.update([schema.question, schema.response])
            elif m in [Evals.CONTEXT_RELEVANCE]:
                req_attrs.update([schema.question, schema.context])
            elif m == Evals.CRITIQUE_LANGUAGE or isinstance(m, CritiqueTone):
                req_attrs.update([schema.response])

            if isinstance(m, ParametricEval):
                ser_metrics.append({"check_name": m.__class__.__name__, **m.dict()})
            elif isinstance(m, Evals):
                ser_metrics.append(m.value)
            else:
                raise ValueError(f"Invalid metric: {m}")
        for idx, row in enumerate(data):
            if not req_attrs.issubset(row.keys()):
                raise ValueError(
                    f"Row {idx} is missing required all required attributes for evaluation: {req_attrs}"
                )

        # send in chunks of 50, so the connection doesn't time out waiting for the server
        results = []
        NUM_TRIES, BATCH_SIZE = 3, 50
        for i in range(0, len(data), BATCH_SIZE):
            response_json = None
            for try_num in range(NUM_TRIES):
                try:
                    logger.info(
                        f"Sending evaluation request for rows {i} to <{i+BATCH_SIZE} to the Uptrain server"
                    )
                    response = self.client.post(
                        url,
                        json={
                            "data": data[i : i + BATCH_SIZE],
                            "checks": [m.value for m in checks],  # type: ignore
                            "metadata": {"project": project_name, **metadata},
                        },
                    )
                    response_json = raise_or_return(response)
                    break
                except Exception as e:
                    logger.info("Retrying evaluation request")
                    if try_num == NUM_TRIES - 1:
                        logger.error(f"Evaluation failed with error: {e}")
                        raise e

            if response_json is not None:
                results.extend(response_json)

        return results

    def download_project_eval_results(self, project_name: str, fpath: str):
        """Fetch all the evaluation results for a project.

        Args:
            project_name: Name of the project to fetch results for.
            fpath: Path to save the results to.
        """
        url = f"{self.base_url}/log_and_evaluate/{project_name}"
        with self.client.stream("GET", url) as response:
            if not response.is_success:
                logger.error(response.text)
                response.raise_for_status()
            else:
                with open(fpath, "w") as download_file:
                    for chunk in response.iter_text():
                        download_file.write(chunk)
