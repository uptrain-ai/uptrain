"""
Implement oeprators over text data.
"""

from __future__ import annotations

import json
import os
import typing as t

from pydantic import BaseModel
import polars as pl
from sqlglot import parse

from uptrain.utilities.sql_utils import extract_tables_and_columns, extract_tables_and_columns_from_create

if t.TYPE_CHECKING:
    from uptrain.framework.config import *
from uptrain.operators.base import *

__all__ = ["HasStar", "GetSchemaDefinition", "ParseSQL", "ValidateTables"]


# TODO: define a Table object and dump that into the dataframe
class Table(BaseModel):
    create_table_stmt: str
    table_name: str
    columns: list

# operators to read schema definition from Spider sql dataset
@register_op
class GetSchemaDefinition(BaseModel):
    col_in_schema: str = "schema"
    col_out: str = "schema_def"
    col_out_tables: str = "schema_tables"

    def make_executor(self, settings: t.Optional[Settings] = None):
        return GetSchemaDefinitionExecutor(self, settings)


class GetSchemaDefinitionExecutor(OperatorExecutor):
    op: GetSchemaDefinition

    def __init__(self, op: GetSchemaDefinition, settings: t.Optional[Settings] = None):
        self.op = op

    def __read_schema_definition(self, schema_name) -> (str, str):
        # TODO figure out a better way to set this
        resources_path = "/Users/bhanu/src/uptrain_experiments/llm/spider/database"
        # List to store all CREATE TABLE statements
        create_table_statements = []
        tables_and_columns = {}

        with open(os.path.join(resources_path, f'{schema_name}/schema.sql'), 'r') as file:
            content = file.read()

            # SQL statements are separated by ';'
            statements = content.split(';')

            # Create table statements
            for statement in statements:
                if statement.strip().startswith('CREATE TABLE'):
                    # Add the statement to the list
                    statement = statement.strip()
                    table, columns = extract_tables_and_columns_from_create(parse(statement)[0])
                    tables_and_columns[table] = columns
                    create_table_statements.append(statement)

        return "\n\n".join(create_table_statements), json.dumps(tables_and_columns)

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        schema_names = data.get_column(self.op.col_in_schema)
        results = [self.__read_schema_definition(schema_name) for schema_name in schema_names]
        schemas = [result[0] for result in results]
        tables = [result[1] for result in results]
        return {"output": data.with_columns([pl.Series(self.op.col_out, schemas), pl.Series(self.op.col_out_tables, tables)])}


# parses output SQL and fetch tables, columns etc
@register_op
class ParseSQL(BaseModel):
    col_in_sql: str = "sql"
    col_out_tables: str = "sql_tables"

    def make_executor(self, settings: t.Optional[Settings] = None):
        return ParseSQLExecutor(self, settings)


class ParseSQLExecutor(OperatorExecutor):
    op: ParseSQL

    def __init__(self, op: ParseSQL, settings: t.Optional[Settings] = None):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        sqls = data.get_column(self.op.col_in_sql)
        tables = []
        for sql in sqls:
            tables.append(json.dumps(extract_tables_and_columns(parse(sql)[0])))

        return {"output": data.with_columns([pl.Series(self.op.col_out_tables, tables)])}


# Ensures that table names from response are valid tables
@register_op
class ValidateTables(BaseModel):
    col_in_response_tables: str = "response_tables"
    col_in_schema_tables: str = "schema_tables"
    col_out_tables_valid: str = "tables_valid"
    col_out_cols_valid: str = "cols_valid"

    def make_executor(self, settings: t.Optional[Settings] = None):
        return ValidateTablesExecutor(self, settings)


class ValidateTablesExecutor(OperatorExecutor):
    op: ValidateTables

    def __init__(self, op: ValidateTables, settings: t.Optional[Settings] = None):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        response_tables = data.get_column(self.op.col_in_response_tables)
        schema_tables = data.get_column(self.op.col_in_schema_tables)
        results = []
        results_column = []
        for response_table, schema_table in zip(response_tables, schema_tables):
            is_valid_table = True
            is_valid_column = True
            # deserialize json
            s = json.loads(schema_table)
            r = json.loads(response_table)
            for table, columns in r.items():
                is_valid_table = is_valid_table and table in s
                is_valid_column = is_valid_column and is_valid_table and set(columns).issubset(set(s[table]))

            results.append(is_valid_table)
            results_column.append(is_valid_column)
        return {"output": data.with_columns([pl.Series(self.op.col_out_tables_valid, results), pl.Series(self.op.col_out_cols_valid, results_column)])}


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
