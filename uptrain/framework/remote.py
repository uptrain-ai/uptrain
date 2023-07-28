"""
This module implements a simple client that can be used to schedule unit-tests/evaluations 
on the UpTrain server. 

"""
# TODO: add user defined custom evaluations (maybe ship the full code to the server?)

import typing as t

from loguru import logger
import httpx

from uptrain.framework.checks import CheckSet, ExperimentArgs
from uptrain.framework.base import Settings
from uptrain.utilities import to_py_types


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
        self.client = httpx.Client(headers={"uptrain-access-token": api_key})

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

    def add_run(self, dataset: str, checkset: str) -> dict:
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

    def get_run(self, run_id: str) -> str:
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

    def add_daily_schedule(self, checkset: str, start_on: str) -> dict:
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

    def get_schedule(self, schedule_id: str) -> str:
        """Get the status of a schedule.

        Args:
            schedule_id: unique identifier for the run.

        Returns:
            run: information about the schedule along with a unique identifier.
        """
        url = f"{self.base_url}/schedule/{schedule_id}"
        response = self.client.get(url)
        return raise_or_return(response)

    def remove_schedule(self, schedule_id: str) -> str:
        """Remove a schedule.

        Args:
            schedule_id: unique identifier for the run.

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
