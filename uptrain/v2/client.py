"""
Client object to send evaluation requests to the UpTrain server.
"""

from __future__ import annotations
import enum
import typing as t

from loguru import logger
from pydantic import BaseModel
import httpx
import pandas as pd


class DataSchema(BaseModel):
    id_: str = "id"
    question: str = "question"
    response: str = "response"
    context: str = "context"
    ground_truth: str = "ground_truth"


class Metric(enum.Enum):
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

    def __init__(
        self, api_key: str, server_url: str = "https://demo.uptrain.ai"
    ) -> None:
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

    def evaluate(
        self,
        project_name: str,
        data: t.Union[pd.DataFrame, list[dict]],
        metrics: list[t.Union[str, Metric]],
        schema: t.Union[DataSchema, dict[str, str], None] = None,
        metadata: t.Optional[dict[str, t.Any]] = None,
    ):
        """Run an evaluation on the server.

        Args:
            project_name: Name of the project to evaluate on.
            data: Data to evaluate on. Either a Pandas DataFrame or a list of dicts.
            metrics: List of metrics to evaluate on.
            schema: Schema of the data. Only required if the data attributes aren't typical (question, response, context).
            metadata: Attributes to attach to this dataset. Useful for filtering and grouping in the UI.
        """
        url = f"{self.base_url}/evaluate_v2"

        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient="records")

        if schema is None:
            schema = DataSchema()
        elif isinstance(schema, dict):
            schema = DataSchema(**schema)

        if metadata is None:
            metadata = {}

        metrics = [Metric(m) if isinstance(m, str) else m for m in metrics]
        req_attrs = set()
        for m in metrics:
            if m == Metric.CONTEXT_RELEVANCE:
                req_attrs.update([schema.question, schema.context])
            elif m == Metric.FACTUAL_ACCURACY:
                req_attrs.update([schema.response, schema.context])
            elif m == Metric.RESPONSE_RELEVANCE:
                req_attrs.update([schema.question, schema.response])
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
                            "metrics": [m.value for m in metrics],  # type: ignore
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

    def download_project_results(self, project_name: str, fpath: str):
        """Fetch all the evaluation results for a project.

        Args:
            project_name: Name of the project to fetch results for.
        """
        url = f"{self.base_url}/evaluate_v2/{project_name}"
        with self.client.stream("GET", url) as response:
            if not response.is_success:
                logger.error(response.text)
                response.raise_for_status()
            else:
                with open(fpath, "w") as download_file:
                    for chunk in response.iter_text():
                        download_file.write(chunk)
