"""IO operators to read from MongoDB."""

from __future__ import annotations
import typing as t
import io

import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.utilities import lazy_load_dep


Mongo_Client = lazy_load_dep("pymongo.mongo_client", "pymongo")


@register_op
class MongoDBReader(TransformOp):
    """Read data from a Mongo Database

    NOTE: To use this operator, you must include the connection string and database in
    the settings, using the key `mongo_db_connection_uri` and 'mongo_db_database_name' respectively.

    Attributes:
        table (str): Table name from where the data needs to be fetched
        query (dict): Conditons on different columns 
        filter (dict): Choosing the relevant columns       

    Example:
        ```python
        from uptrain.operators.io import MongoDBReader

        table = customer_table
        query = {column_name: "condition"}
        filter = {'_id': 0, 'title': 1, 'date': 1}
        reader = MongoDBReader(
            table = table,
            query = query,
            filter = filter
        )
        output = reader.setup().run()["output"]
        ```
    """
    table: str
    query: t.Optional[dict] = dict()
    filter: t.Optional[dict[str, str]] = dict()
    limit_rows: int | None = None

    def setup(self, settings: Settings):
        connection_uri = settings.check_and_get("mongo_db_connection_uri")
        self._client = Mongo_Client.MongoClient(connection_uri)
        self._db = self._client[settings.check_and_get("mongo_db_database_name")]
        return self

    def run(self) -> TYPE_TABLE_OUTPUT:
        table = self._db[self.table]
        if self.limit_rows is None:
            rows = table.find(self.query, self.filter)
        else:
            rows = table.find(self.query, self.filter).limit(self.limit_rows)
       
        return {"output": pl.from_dicts(rows)}

