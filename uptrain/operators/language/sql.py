"""
Implement oeprators over text data.
"""

from __future__ import annotations

import os
import re
import typing as t
from urllib.parse import urlparse

from loguru import logger
from pydantic import BaseModel, Field
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework.config import *
from uptrain.operators.base import *

__all__ = ["HasStar", "GetSchemaDefinition"]


# operators to read schema definition from Spider sql dataset
@register_op
class GetSchemaDefinition(BaseModel):
    col_in_schema: str = "schema"
    col_out: str = "schema_def"

    def make_executor(self, settings: t.Optional[Settings] = None):
        return GetSchemaDefinitionExecutor(self, settings)


class GetSchemaDefinitionExecutor(OperatorExecutor):
    op: GetSchemaDefinition

    def __init__(self, op: GetSchemaDefinition, settings: t.Optional[Settings] = None):
        self.op = op

    def __read_schema_definition(self, schema_name) -> str:
        # TODO figure out a better way to set this
        resources_path = "/Users/bhanu/src/uptrain_experiments/llm/spider/database"
        # List to store all CREATE TABLE statements
        create_table_statements = []

        with open(os.path.join(resources_path, f'{schema_name}/schema.sql'), 'r') as file:
            content = file.read()

            # SQL statements are separated by ';'
            statements = content.split(';')

            # Create table statements
            for statement in statements:
                if statement.strip().startswith('CREATE TABLE'):
                    # Add the statement to the list
                    create_table_statements.append(statement.strip())
        return "\n\n".join(create_table_statements)

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        schema_names = data.get_column(self.op.col_in_schema)
        results = [self.__read_schema_definition(schema_name) for schema_name in schema_names]
        return {"output": data.with_columns([pl.Series(self.op.col_out, results)])}


# Check if SQL has star
@register_op
class HasStar(BaseModel):
    col_in_text: str = "text"
    col_out: str = get_output_col_name_at(0)

    def make_executor(self, settings: t.Optional[Settings] = None):
        return HasStarExecutor(self)


class HasStarExecutor(OperatorExecutor):
    op: HasStar

    def __init__(self, op: HasStar):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        sqls = data.get_column(self.op.col_in_text)
        results = ["*" in sql for sql in sqls]
        return {"output": data.with_columns([pl.Series(self.op.col_out, results)])}
