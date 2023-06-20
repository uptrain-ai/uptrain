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


def extract_tables_and_columns(expression: Expression):
    tables = defaultdict(set)
    if isinstance(expression, Table) and expression.this.this not in tables:
        tables[expression.this.this] = set([])

    # iterate through all args keys
    for key, e in expression.iter_expressions():
        merge_dictionaries(tables, extract_tables_and_columns(e))
    if isinstance(expression, Column):
        table = expression.table or PLACEHOLDER_TABLE
        if table not in tables:
            tables[table] = set([])
        tables[table].add(expression.this.this)
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
