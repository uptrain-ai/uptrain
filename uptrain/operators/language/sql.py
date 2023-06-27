"""
Implement oeprators over sql data.
"""

from __future__ import annotations

import itertools
import json
import os
import typing as t

from pydantic import BaseModel
import polars as pl

from uptrain.utilities import lazy_load_dep
from uptrain.utilities.sql_utils import extract_tables_and_columns, extract_tables_and_columns_from_create, \
    PLACEHOLDER_TABLE, execute_and_compare_sql

if t.TYPE_CHECKING:
    from uptrain.framework.base import *
from uptrain.operators.base import *

sqlglot = lazy_load_dep("sqlglot", "sqlglot")

__all__ = ["HasStar", "ParseCreateStatements", "ParseSQL", "ValidateTables", "ExecuteSQL"]


# TODO: define a Table object and dump that into the dataframe
class Table(BaseModel):
    create_table_stmt: str
    table_name: str
    columns: list


# Read tables and columns information from CREATE TABLE statements
@register_op
class ParseCreateStatements(TableOp):
    col_in_schema_def: str
    col_out_tables: str

    def setup(self, settings: t.Optional[Settings] = None):
        return self

    def __fetch_tables_columns(self, create_statements) -> (str, str, str):
        tables_and_columns = {}
        # SQL statements are separated by ';'
        statements = create_statements.split(';')

        # Create table statements
        for statement in statements:
            if statement.upper().strip().startswith('CREATE TABLE'):
                # Add the statement to the list
                statement = statement.strip()
                # TODO: handle input database dialect instead of assuming it.
                parsed = sqlglot.parse(statement, read=sqlglot.Dialects.SQLITE)
                table, columns = extract_tables_and_columns_from_create(parsed[0])
                tables_and_columns[table] = list(columns)

        return json.dumps(tables_and_columns)

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        schemas = data.get_column(self.col_in_schema_def)
        tables = [self.__fetch_tables_columns(schema) for schema in schemas]
        return {"output": data.with_columns([pl.Series(self.col_out_tables, tables)])}


# parses output SQL and fetch tables, columns etc
@register_op
class ParseSQL(TableOp):
    col_in_sql: str
    col_out_tables: str
    col_out_is_valid_sql: str

    def setup(self, _: t.Optional[Settings] = None):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        sqls = data.get_column(self.col_in_sql)
        tables = []
        is_valid = []
        for sql in sqls:
            try:
                # TODO: parse using expected dialect
                parsed = sqlglot.parse(sql)
                tables_and_columns = extract_tables_and_columns(parsed[0])
                # Since sets are not serializable, convert to list
                for table, columns in tables_and_columns.items():
                    tables_and_columns[table] = list(columns)
                tables.append(json.dumps(tables_and_columns))
                is_valid.append(True)
            except sqlglot.errors.ParseError:
                tables.append(json.dumps({}))
                is_valid.append(False)

        return {"output": data.with_columns([pl.Series(self.col_out_tables, tables),
                                             pl.Series(self.col_out_is_valid_sql, is_valid)])}


# Ensures that table names from response are valid tables
@register_op
class ValidateTables(TableOp):
    col_in_response_tables: str
    col_in_schema_tables: str
    col_out_is_tables_valid: str
    col_out_is_cols_valid: str

    def setup(self, _: t.Optional[Settings] = None):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        response_tables = data.get_column(self.col_in_response_tables)
        schema_tables = data.get_column(self.col_in_schema_tables)
        results = []
        results_column = []
        for response_table, schema_table in zip(response_tables, schema_tables):
            is_valid_table = True
            is_valid_column = True
            # deserialize json
            s = json.loads(schema_table)
            r = json.loads(response_table)
            columns_list = [columns for table, columns in s.items()]
            all_columns = set(itertools.chain(*columns_list))
            for table, columns in r.items():
                is_valid_table &= table == PLACEHOLDER_TABLE or table in s
                # TODO: handle aliases and do lineage check
                is_valid_column = is_valid_column and is_valid_table and \
                                   ((table != PLACEHOLDER_TABLE and set(columns).issubset(set(s[table]))) or
                                    (table == PLACEHOLDER_TABLE and set(columns).issubset(all_columns)))

            results.append(is_valid_table)
            results_column.append(is_valid_column)
        return {"output": data.with_columns(
            [pl.Series(self.col_out_is_tables_valid, results), pl.Series(self.col_out_is_cols_valid, results_column)])}


@register_op
class ExecuteSQL(TableOp):
    col_in_response_sql: str
    col_in_gt_sql: str
    col_in_db_path: str
    col_out_execution_accuracy: str

    def setup(self, settings: t.Optional[Settings] = None):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        response_sqls = data.get_column(self.col_in_response_sql)
        gt_sqls = data.get_column(self.col_in_gt_sql)
        db_paths = data.get_column(self.col_in_db_path)
        results = []
        for response_sql, gt_sql, db_path in zip(response_sqls, gt_sqls, db_paths):
            results.append(execute_and_compare_sql(response_sql, gt_sql, db_path))
        return {"output": data.with_columns([pl.Series(self.col_out_execution_accuracy, results)])}


# Check if SQL has star
@register_op
class HasStar(TableOp):
    col_in_text: str
    col_out: str

    def setup(self, _: t.Optional[Settings] = None):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        sqls = data.get_column(self.col_in_text)
        results = ["*" in sql for sql in sqls]
        return {"output": data.with_columns([pl.Series(self.col_out, results)])}
