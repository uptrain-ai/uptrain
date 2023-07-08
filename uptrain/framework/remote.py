"""
This module implements a simple client that can be used to schedule unit-tests/evaluations 
on the UpTrain server. 

"""
# TODO: add user defined custom evaluations (maybe ship the full code to the server?)

import typing as t

from loguru import logger
import httpx

from uptrain.framework.checks import CheckSet
from uptrain.framework.base import Settings


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
            if not response.is_success:
                raise RuntimeError(
                    f"Failed to authenticate with the Uptrain server: {response.json()}"
                )
            else:
                return response.json()
        except httpx.ConnectError as e:
            raise RuntimeError(
                f"Failed to connect to the Uptrain server at {self.base_url}"
            ) from e

    def add_dataset(self, name: str, fpath: str):
        url = f"{self.base_url}/dataset"
        with open(fpath, "rb") as file:
            files = {"data_file": (name, file, "application/octet-stream")}
            response = self.client.post(url, data={"name": name}, files=files)
        return response.json()

    def get_dataset(self, name: str, version: t.Optional[int] = None):
        url = f"{self.base_url}/dataset"
        params: dict = {"name": name}
        if version is not None:
            params["version"] = version
        response = self.client.get(url, params=params)
        return response.json()

    def list_datasets(self, skip: int = 0, limit: int = 100):
        url = f"{self.base_url}/datasets"
        params = {"skip": skip, "limit": limit}
        response = self.client.get(url, params=params)
        return response.json()

    def add_checkset(self, name: str, checkset: CheckSet, settings: Settings):
        url = f"{self.base_url}/checkset"
        response = self.client.post(
            url,
            json={"name": name, "config": checkset.dict(), "settings": settings.dict()},
        )
        return response.json()

    def get_checkset(self, name: str, version: t.Optional[int] = None):
        url = f"{self.base_url}/checkset"
        params: dict = {"name": name}
        if version is not None:
            params["version"] = version
        response = self.client.get(url, params=params)
        return response.json()

    def list_checksets(self, skip: int = 0, limit: int = 10):
        url = f"{self.base_url}/checksets"
        params = {"skip": skip, "limit": limit}
        response = self.client.get(url, params=params)
        return response.json()

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
        return response.json()

    def get_run(self, run_id: str) -> str:
        """Get the status of a run.

        Args:
            run_id: unique identifier for the run.

        Returns:
            run: information about the run along with a unique identifier.
        """
        url = f"{self.base_url}/run/{run_id}"
        response = self.client.get(url)
        return response.json()

    def list_runs(self, num: int = 10, only_completed: bool = False):
        """List all the runs on the server.

        - filter by scheduled/completed/in-process?
        """
        url = f"{self.base_url}/runs"
        params: dict = {"num": num}
        if only_completed:
            params["status"] = "completed"
        response = self.client.get(url, params=params)
        return response.json()
