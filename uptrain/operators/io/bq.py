"""IO operators to read/write from/to Bigquery."""

from __future__ import annotations
import typing as t
import io

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
    limit_rows: int | None = None

    def setup(self, settings: Settings):
        from google.oauth2 import service_account

        gcp_sa_creds = settings.check_and_get("gcp_service_account_credentials")
        credentials = service_account.Credentials.from_service_account_info(
            gcp_sa_creds
        )
        self._client = bigquery.Client(credentials=credentials)
        return self

    def run(self) -> TYPE_TABLE_OUTPUT:
        if self.limit_rows is None:
            query_job = self._client.query(self.query)
        else:
            query_job = self._client.query(self.query + " LIMIT " + str(self.limit_rows))
        rows = query_job.result()
        return {"output": pl.from_arrow(rows.to_arrow())}


@register_op
class BigQueryWriter(TransformOp):
    """Write data to a bigquery table.

    NOTE: To use this operator, you must include the GCP service account credentials in
    the settings, using the key `gcp_service_account_credentials`.

    Attributes:
        project_name (str): Name of the project to add to.
        table_name (str): Name of the table to add to. Final destination is project_name + table_name.
        update_query (str): Optional query if one want to update an existing table with the evaluation results.
        delete_query (str): Optional query if one wants to delete the newly created table (after update).

    Example:
        ```python
        from uptrain.operators.io import BigQueryWriter

        writer = BigQueryWriter(
            project_name="project",
            table_name="dataset.temp_table",
            update_query="UPDATE `{project}.{dataset}.{table}` AS target SET target.score = temp.score FROM `{project}.{dataset}.temp_table` AS temp WHERE target.id = temp.id;
            delete_query="DROP TABLE `project.dataset.temp_table`"
        )
        writer.setup(settings).run()
        ```
    """

    project_name: str
    table_name: str
    update_query: t.Union[str, None] = None
    delete_query: t.Union[str, None] = None

    def setup(self, settings: Settings):
        from google.oauth2 import service_account

        gcp_sa_creds = settings.check_and_get("gcp_service_account_credentials")
        credentials = service_account.Credentials.from_service_account_info(
            gcp_sa_creds
        )
        self._client = bigquery.Client(credentials=credentials)
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:

        with io.BytesIO() as stream:
            data.write_parquet(stream)
            stream.seek(0)
            query_job = self._client.load_table_from_file(
                stream,
                destination=self.table_name,
                project=self.project_name,
                job_config=bigquery.LoadJobConfig(
                    source_format=bigquery.SourceFormat.PARQUET,
                ),
            )
        query_job.result()  # Waits for the job to complete

        if self.update_query is not None:
            query_job = self._client.query(self.update_query)
            query_job.result()

        if self.delete_query is not None:
            query_job = self._client.query(self.delete_query)
            query_job.result()

        return {"output": data}