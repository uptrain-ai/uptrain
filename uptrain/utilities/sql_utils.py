import sqlite3
from collections import defaultdict
from typing import Dict, Any, Set

import numpy as np
import polars as pl

from sqlglot import Expression
from sqlglot.expressions import Table, Column, ColumnDef, Create, Schema

from loguru import logger

PLACEHOLDER_TABLE = "PLACEHOLDER_TABLE"


def merge_dictionaries(dict1: Dict[Any, Set], dict2: Dict[Any, Set]):
    for key, value in dict2.items():
        if key in dict1:
            dict1[key] = dict1[key].union(value)
        else:
            dict1[key] = value

    return dict1


def extract_tables_and_columns(expression: Expression, alias_mapping=None):
    if alias_mapping is None:
        alias_mapping = {}

    tables = defaultdict(set)

    # Handle tables and table aliases
    if isinstance(expression, Table):
        table_key = f"{expression.db}.{expression.name}" if expression.db else expression.name
        if table_key not in tables:
            tables[table_key] = set([])
        if expression.alias:
            alias_mapping[expression.alias] = table_key

    for key, e in expression.iter_expressions():
        merge_dictionaries(tables, extract_tables_and_columns(e, alias_mapping))

    # Handle columns and their associated tables or table aliases
    if isinstance(expression, Column):
        table = f"{expression.db}.{expression.table}" if expression.db else expression.table
        if table and table in alias_mapping:
            table = alias_mapping[table]
        table = table or PLACEHOLDER_TABLE
        if table not in tables:
            tables[table] = set([])
        tables[table].add(expression.name)

    # Merge aliases
    # TODO: this does not work if table1 is alias of table2 which is an alias of table3
    for table in tables:
        if table in alias_mapping:
            true_table = alias_mapping[table]
            tables[true_table] = tables[true_table].union(tables[table])

    # remove alias tables
    for table in alias_mapping:
        if table in tables:
            del tables[table]
    return tables


def extract_tables_and_columns_from_create(expression: Create):
    schema: Schema = expression.this
    table = schema.this
    table_name = table.name
    columns = set([])
    for e in schema.expressions:
        if isinstance(e, ColumnDef):
            columns.add(e.name)
    return table_name, columns


def run_query(query, connection):
    cursor = connection.cursor()
    cursor.execute(query)

    # Get data and column names from the cursor
    data = cursor.fetchall()
    columns = [description[0] for description in cursor.description]

    df = pl.DataFrame(data, columns)
    return df


# Execute predicted SQL, ground truth and compute execution accuracy of the predicted sql. We assume these queries to be
# read queries.
def execute_and_compare_sql(predicted_sql, ground_truth, db_path, ignore_column_order=True, ignore_row_order=True):
    conn = sqlite3.connect(db_path)
    res = False
    try:
        # Run the queries
        pred_df = run_query(predicted_sql, conn)
        gt_df = run_query(ground_truth, conn)

        # Close the connection
        conn.close()

        if ignore_column_order:
            # Bring the columns to the same order
            pred_df = pred_df.select(sorted(pred_df.columns, key=str.lower))
            gt_df = gt_df.select(sorted(gt_df.columns, key=str.lower))

        if ignore_row_order:
            # Sort the dataframe rows to ignore row order
            pred_df = pred_df.sort(list(pred_df.columns))
            gt_df = gt_df.sort(list(gt_df.columns))

        res = np.array_equal(pred_df.to_numpy(), gt_df.to_numpy())
    except Exception as e:
        logger.warning(f"Error executing: {e}")
        pass
    return res

