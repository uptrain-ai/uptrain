"""
This module implements a simple client that can be used to schedule unit-tests/evaluations 
on the UpTrain server. 

- TODO: add user defined custom evaluations (maybe ship the full code to the server?)
"""

from dataclasses import dataclass
import typing as t

from loguru import logger
import httpx

from uptrain.framework.checks import CheckSet


@dataclass
class DatasetsAPI:
    base_url: str
    client: httpx.Client

    def add(self, name: str, fpath: str):
        url = f"{self.base_url}/dataset"
        with open(fpath, "rb") as file:
            files = {"data_file": (name, file, "application/octet-stream")}
            response = self.client.post(url, data={"name": name}, files=files)
        return response.json()

    def get(self, name: str, version: t.Optional[int] = None):
        url = f"{self.base_url}/dataset"
        params = {"name": name}
        if version is not None:
            params["version"] = version
        response = self.client.get(url, params=params)
        return response.json()

    def list(self, skip: int = 0, limit: int = 100):
        url = f"{self.client.base_url}/datasets"
        params = {"skip": skip, "limit": limit}
        response = self.client.get(url, params=params)
        return response.json()


@dataclass
class ChecksetsAPI:
    base_url: str
    client: httpx.Client

    def add(self, name: str, checkset: CheckSet):
        url = f"{self.base_url}/checkset"
        response = self.client.post(url, json={"name": name, "config": checkset.dict()})
        return response.json()

    def get(self, name: str, version: t.Optional[int] = None):
        url = f"{self.base_url}/checkset"
        params = {"name": name}
        if version is not None:
            params["version"] = version
        response = self.client.get(url, params=params)
        return response.json()

    def list(self, skip: int = 0, limit: int = 100):
        url = f"{self.base_url}/checksets"
        params = {"skip": skip, "limit": limit}
        response = self.client.get(url, params=params)
        return response.json()


class APIClient:
    base_url: str
    client: httpx.Client
    datasets: DatasetsAPI
    checksets: ChecksetsAPI

    def __init__(self, server_url: str = "http://localhost:4300") -> None:
        self.base_url = server_url.rstrip("/") + "/api/public"
        self.client = httpx.Client()
        self.datasets = DatasetsAPI(base_url=self.base_url, client=self.client)
        self.checksets = ChecksetsAPI(base_url=self.base_url, client=self.client)

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

    def get_run_status(self, run_id: str) -> str:
        """Get the status of a run.

        Args:
            run_id: unique identifier for the run.

        Returns:
            run: information about the run along with a unique identifier.
        """
        url = f"{self.base_url}/run/{run_id}"
        response = self.client.get(url)
        return response.json()

    def list_all_active_runs(self):
        """List all runs on the server.

        - filter by scheduled/completed/in-process?
        - filter by timestamp?
        """
        ...

    def cancel_active_run(self):
        """Cancel an active run on the server."""
        ...

    def get_logs_for_run(self):
        """Get logs for a run."""
        ...

    def get_results_for_run(self):
        """Get results for a run."""
        ...