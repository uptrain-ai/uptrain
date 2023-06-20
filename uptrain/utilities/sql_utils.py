import sqlite3
from collections import defaultdict
from typing import Dict, Any, Set

from sqlglot import Expression
from sqlglot.expressions import Table, Column, ColumnDef, Create, Schema

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
    for table in tables:
        if table in alias_mapping:
            true_table = alias_mapping[table]
            tables[true_table] = tables[true_table].union(tables[table])
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


# Execute predicted SQL, ground truth and compare the result
# From: https://github.com/AlibabaResearch/DAMO-ConvAI/blob/main/bird/llm/src/evaluation.py
def execute_sql(predicted_sql, ground_truth, db_path):
    conn = sqlite3.connect(db_path)
    # Connect to the database
    cursor = conn.cursor()
    cursor.execute(predicted_sql)
    predicted_res = cursor.fetchall()
    cursor.execute(ground_truth)
    ground_truth_res = cursor.fetchall()
    res = 0
    if set(predicted_res) == set(ground_truth_res):
        res = 1
    return res