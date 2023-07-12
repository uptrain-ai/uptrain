"""IO operators to read from Excel files"""

from __future__ import annotations
import typing as t

import polars as pl
import deltalake as dl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.utilities import lazy_load_dep


bigquery = lazy_load_dep("google.cloud.bigquery", "google-cloud-bigquery")


@register_op
class BigqueryReader(TransformOp):
    """Read data from a bigquery table.

    Attributes:
        query (str): Query to run against the BigQuery table.
        col_timestamp (str): Column name to use as the timestamp column. Only used in the context of monitoring.
    """

    query: str
    col_timestamp: str = "timestamp"

    def setup(self, settings: Settings):
        return self

    def run(self) -> TYPE_TABLE_OUTPUT:
        query_job = bigquery.Client().query(self.query)
        rows = query_job.result()
        return {"output": pl.from_arrow(rows.to_arrow())}
