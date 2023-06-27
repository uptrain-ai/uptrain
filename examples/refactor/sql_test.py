import os
from uptrain.framework import CheckSet, Settings, SimpleCheck
from uptrain.io import JsonReader, JsonWriter

from uptrain.operators.language.sql import HasStar, ParseSQL, ValidateTables, ExecuteSQL, GetSchemaDefinition

from uptrain.operators import PlotlyChart

# Define the config
LOGS_DIR = "/tmp/uptrain_logs"


def produce_dataset_w_spider_schema(source_path, sink_path, spider_dataset_path):
    # Populate schema, sqllite file path from spider dataset

    source = JsonReader(fpath=source_path)
    source.setup()
    data = source.run()["output"]

    op = SimpleCheck(
        name="get_schema_check",
        sequence=[
            GetSchemaDefinition(),
        ],
    )
    op.setup(Settings(resources_folder=spider_dataset_path))
    data = op.run(data)

    JsonWriter(fpath=sink_path).run(data)


select_all_check = SimpleCheck(
    name="Query has star symbol",
    sequence=[
        HasStar(
            col_in_text="response",
            col_out="has_star_symbol_in_query"
        ),
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
        ParseSQL(
            col_in_sql="response",
            col_out_tables="response_tables",
            col_out_is_valid_sql="is_sql_valid"
        ),
        ValidateTables(col_in_response_tables="response_tables",
                       col_in_schema_tables="schema_tables",
                       col_out_tables_valid="tables_valid",
                       col_out_cols_valid="cols_valid")
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
        ExecuteSQL(col_in_response_sql="response",
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

    # produce_dataset_w_spider_schema(DATASET_TEXT_TO_SQL, DATASET_TEXT_TO_SQL_OUT, "/tmp/uptrain_resources/")
    DATASET_TEXT_TO_SQL = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../datasets/text_to_sql_sample.jsonl",
    )

    cfg = get_checkset(DATASET_TEXT_TO_SQL)
    cfg.setup()
    cfg.run()

    if args.start_streamlit:
        start_streamlit()
