import os
from uptrain.framework import CheckSet, Settings, SimpleCheck
from uptrain.io import JsonReader, JsonWriter

from uptrain.operators.language.sql import ParseSQL, ValidateTables, ExecuteAndCompareSQL, ParseCreateStatements

from uptrain.operators import PlotlyChart, SelectOp

import polars as pl

from uptrain.operators.language.text import KeywordDetector

# Define the config
LOGS_DIR = "/tmp/uptrain_logs"


# Reads schema definitions from spider dataset. schema definitions are a list of CREATE TABLE Statements
def __read_schema_definition(schema_name, spider_dataset_path) -> (str, str, str):
    # List to store all CREATE TABLE statements
    create_table_statements = []
    db_path = os.path.join(spider_dataset_path, f'database/{schema_name}/{schema_name}.sqlite')

    with open(os.path.join(spider_dataset_path, f'database/{schema_name}/schema.sql'), 'r') as file:
        content = file.read()

        # SQL statements are separated by ';'
        statements = content.split(';')

        # Create table statements
        for statement in statements:
            if statement.upper().strip().startswith('CREATE TABLE'):
                create_table_statements.append(statement.strip())

    return ";\n\n".join(create_table_statements), db_path


def produce_dataset_w_spider_schema(source_path, sink_path, spider_dataset_path):
    # Populate schema, sqllite file path from spider dataset
    # Get spider dataset from https://yale-lily.github.io/spider

    source = JsonReader(fpath=source_path)
    source.setup()
    data = source.run()["output"]

    schema_names = data.get_column("schema")
    results = [__read_schema_definition(schema_name, spider_dataset_path) for schema_name in schema_names]
    schemas = [result[0] for result in results]
    db_paths = [result[1] for result in results]
    data = data.with_columns([pl.Series("schema_def", schemas), pl.Series("db_path", db_paths)])

    JsonWriter(fpath=sink_path).run(data)


select_all_check = SimpleCheck(
    name="Query has star symbol",
    sequence=[
        SelectOp(
            columns={
                "has_star_symbol_in_query": KeywordDetector(
                    col_in_text="response",
                    keyword="*"
                ),
            }
        )
    ],
    plot=[
        PlotlyChart.Histogram(
            title="Distribution: Generated SQL query has '*' symbol",
            props=dict(x="has_star_symbol_in_query", nbins=2, color='model', barmode='group'),
        )
    ],
)

sql_validity_check = SimpleCheck(
    name="Validate SQL",
    sequence=[
        ParseCreateStatements(
            col_in_schema_def="schema_def",
            col_out_tables="schema_tables",
        ),
        ParseSQL(
            col_in_sql="response",
            col_out_tables="response_tables",
            col_out_is_valid_sql="is_sql_valid"
        ),
        ValidateTables(col_in_response_tables="response_tables",
                       col_in_schema_tables="schema_tables",
                       col_out_is_tables_valid="tables_valid",
                       col_out_is_cols_valid="cols_valid")
    ],
    plot=[
        PlotlyChart.Histogram(
            title="Distribution: Generated SQL query is valid - column names",
            props=dict(x="cols_valid", nbins=2, color='model', barmode='group'),
        ),
        PlotlyChart.Histogram(
            title="Distribution: Generated SQL query is valid - table names",
            props=dict(x="tables_valid", nbins=2, color='model', barmode='group'),
        ),
    ],
)

execution_accuracy_check = SimpleCheck(
    name="Generated SQL query execution accuracy",
    sequence=[
        ExecuteAndCompareSQL(col_in_response_sql="response",
                             col_in_gt_sql="gt_query",
                             col_in_db_path="db_path",
                             col_out_execution_accuracy="execution_accuracy")
    ],
    plot=[
        PlotlyChart.Histogram(
            title="Distribution: SQL execution gives correct results",
            props=dict(x="execution_accuracy", nbins=2, color='model', barmode='group'),
        ),
    ],
)


def get_checkset(source_path):
    # Define the config
    checks = [select_all_check, sql_validity_check, execution_accuracy_check]

    return CheckSet(
        source=JsonReader(fpath=source_path),
        checks=checks,
        settings=Settings(logs_folder=LOGS_DIR),
    )


# -----------------------------------------------------------
# Starting a streamlit server to visualize the results
# -----------------------------------------------------------


def start_streamlit():
    from uptrain.dashboard import StreamlitRunner

    runner = StreamlitRunner(LOGS_DIR)
    runner.start()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--start-streamlit", default=True, action="store_true")
    args = parser.parse_args()

    # produce_dataset_w_spider_schema(DATASET_TEXT_TO_SQL, DATASET_TEXT_TO_SQL_OUT, "/tmp/uptrain_resources/spider")
    DATASET_TEXT_TO_SQL = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../datasets/text_to_sql_sample.jsonl",
    )

    cfg = get_checkset(DATASET_TEXT_TO_SQL)
    cfg.setup()
    cfg.run()

    if args.start_streamlit:
        start_streamlit()
