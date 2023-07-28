"""IO operators to read/write from/to Bigquery."""

from __future__ import annotations
import typing as t

import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.utilities import lazy_load_dep


bigquery = lazy_load_dep("google.cloud.bigquery", "google-cloud-bigquery")


@register_op
class BigQueryReader(TransformOp):
    """Read data from a bigquery table.

    NOTE: To use this operator, you must include the GCP service account credentials in
    the settings, using the key `gcp_service_account_credentials`.

    Attributes:
        query (str): Query to run against the BigQuery table.
        col_timestamp (str): Column name to use as the timestamp column. Only used in the context of monitoring.

    Example:
        ```python
        from uptrain.operators.io import BigQueryReader

        query = "SELECT * FROM `bigquery-public-data.samples.shakespeare` LIMIT 10"
        reader = BigQueryReader(
            query=query,
            col_timestamp="timestamp"
        )
        output = reader.setup().run()["output"]
        ```
    """

    query: str
    col_timestamp: str = "timestamp"

    def setup(self, settings: Settings):
        from google.oauth2 import service_account

        gcp_sa_creds = settings.check_and_get("gcp_service_account_credentials")
        credentials = service_account.Credentials.from_service_account_info(
            gcp_sa_creds
        )
        self._client = bigquery.Client(credentials=credentials)
        return self

    def run(self) -> TYPE_TABLE_OUTPUT:
        query_job = self._client.query(self.query)
        rows = query_job.result()
        return {"output": pl.from_arrow(rows.to_arrow())}
