import sqlite3
from collections import defaultdict
from typing import Dict, Any, Set

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


# Execute predicted SQL, ground truth and compute execution accuracy of the predicted sql
# From: https://github.com/AlibabaResearch/DAMO-ConvAI/blob/main/bird/llm/src/evaluation.py
def execute_sql(predicted_sql, ground_truth, db_path):
    conn = sqlite3.connect(db_path)
    # Connect to the database
    cursor = conn.cursor()
    # TODO read output as dataframe and compare based on columns
    # TODO change return value to boolean
    res = 0
    try:
        cursor.execute(predicted_sql)
        predicted_res = cursor.fetchall()
        cursor.execute(ground_truth)
        ground_truth_res = cursor.fetchall()
        if set(predicted_res) == set(ground_truth_res):
            res = 1
    except Exception as e:
        logger.warning(f"Error executing: {e}")
        pass
    return res


if __name__ == "__main__":
    # Issue: Selects country as French instead of France
    predicted_sql = """
    SELECT AVG(Age), MIN(Age), MAX(Age)
FROM singer
WHERE Country = 'French'"""
    gt_query = """
    SELECT avg(age) ,  min(age) ,  max(age) FROM singer WHERE country  =  'France'
    """
    res = execute_sql(predicted_sql, gt_query, "/Users/bhanu/src/uptrain_experiments/llm/spider/database/concert_singer/concert_singer.sqlite")
    print(res)

    # Issue: selects wrong column
    predicted_sql = """
        SELECT s.Name, s.Song_release_year
FROM singer s
WHERE s.Age = (SELECT MIN(Age) FROM singer)
LIMIT 1;"""
    gt_query = """
        SELECT song_name ,  song_release_year FROM singer ORDER BY age LIMIT 1
        """
    res = execute_sql(predicted_sql, gt_query,
                      "/Users/bhanu/src/uptrain_experiments/llm/spider/database/concert_singer/concert_singer.sqlite")
    print(res)


    # Issue: incorrect order of select columns
    predicted_sql = "SELECT City, COUNT(Employee_ID) AS num_employees FROM employee GROUP BY City;"
    gt_query = "SELECT count(*) ,  city FROM employee GROUP BY city"
    res = execute_sql(predicted_sql, gt_query,
                      "/Users/bhanu/src/uptrain_experiments/llm/spider/database/employee_hire_evaluation/employee_hire_evaluation.sqlite")
    print(res)


    # Issue: incorrect GT query
    predicted_sql = "SELECT Name FROM teacher WHERE Hometown <> 'Little Lever Urban District'"
    gt_query = "select name from teacher where hometown != \"little lever urban district\""
    res = execute_sql(predicted_sql, gt_query,
                      "/Users/bhanu/src/uptrain_experiments/llm/spider/database/course_teach/course_teach.sqlite")
    print(res)
