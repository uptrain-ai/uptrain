import openai
import copy

from uptrain.framework.config import Config, Settings, SimpleCheck
from uptrain.io import JsonReader, JsonWriter
from uptrain.operators import PlotlyChart
from regression_testing.experiment import ExperimentManager
from uptrain.operators.language import TextLength
from uptrain.operators.language.sql import HasStar, ParseSQL, ValidateTables, ExecuteSQL

prompt_template = """
    You are a {persona} whose job is to only output SQL command for a given question in {dialect} SQL dialect. Do not output anything other than the SQL command.
    
    Here is the create table commands for my database:
    {schema_def}
    
    {question}
    
    SQL:
"""

user_inputs = {
    'experiment_args': {
        "prompt_templates": [prompt_template],
        "model_names": ["gpt-3.5-turbo"],
        "comparison_args": [{
            "comparison_variables": 'persona',
            'comparison_options': ['SQL expert', 'Data Engineer']
        }],
    },
    'dataset_args': {
        'file_name': "/Users/bhanu/src/uptrain_experiments/llm/SQL_small.jsonl",
        'input_variables': ['question', 'schema_def', 'dialect'],
    },
    'evaluation_args': None
}


LOGS_DIR = "/Users/bhanu/src/uptrain/examples/refactor/uptrain_logs"


def get_config():
    # Define the config
    checks = []

    # Compute all the embeddings - question, document, response
    checks.append(SimpleCheck(
        name="has_star",
        compute=[
            HasStar(col_in_text="response",
                    col_out="has_star"),
        ],
        source=JsonReader(fpath="{experiment_path}/output.jsonl"),
        sink=JsonWriter(fpath="{experiment_path}/interim_data/has_star.jsonl"),
        plot=PlotlyChart(kind="histogram", title="Distribution of has star", props=dict(x="has_star"))
    ))

    checks.append(
        SimpleCheck(
            name="Validate SQL",
            compute=[
                ParseSQL(
                    col_in_sql="response",
                    col_out_tables="response_tables",
                    col_out_is_valid_sql="is_sql_valid"
                )
            ],
            source=JsonReader(fpath="{experiment_path}/interim_data/has_star.jsonl"),
            sink=JsonWriter(fpath="{experiment_path}/interim_data/parse_sql.jsonl"),
            plot=PlotlyChart(
                kind="histogram",
                title="Distribution: is sql valid",
                props=dict(x="is_sql_valid"),
            ),
        )
    )
    # TODO: fix, add column valid stuff. May be add an invalid column'
    # TODO: add an example where this check fails
    checks.append(
        SimpleCheck(
            name="Check table and columns",
            compute=[
                ValidateTables(col_in_response_tables="response_tables",
                               col_in_schema_tables="schema_tables",
                               col_out_tables_valid="tables_valid",
                               col_out_cols_valid="cols_valid")
            ],
            source=JsonReader(fpath="{experiment_path}/interim_data/parse_sql.jsonl"),
            sink=JsonWriter(fpath="{experiment_path}/interim_data/validate_entities.jsonl"),
            plot=PlotlyChart(
                kind="histogram",
                title="Distribution of valid tables",
                props=dict(x="tables_valid"),
            ),
        )
    )

    checks.append(
        SimpleCheck(
            name="Execution Accuracy",
            compute=[
                ExecuteSQL(col_in_response_sql="response",
                           col_in_gt_sql="gt_query",
                           col_in_db_path="db_path",
                           col_out_execution_accuracy="execution_accuracy")
            ],
            source=JsonReader(fpath="{experiment_path}/interim_data/validate_entities.jsonl"),
            sink=JsonWriter(fpath="{experiment_path}/interim_data/exec_accuracy.jsonl"),
            plot=PlotlyChart(
                kind="histogram",
                title="Distribution of Execution accuracy",
                props=dict(x="execution_accuracy"),
            ),
        )
    )

    # TODO: plot without compute?
    checks.append(
        SimpleCheck(
            name="Show outputs",
            compute=[TextLength(
                col_in_text="response",
                col_out="sql_length",
            )],
            source=JsonReader(fpath="{experiment_path}/interim_data/exec_accuracy.jsonl"),
            sink=JsonWriter(fpath="{experiment_path}/interim_data/show_outputs.jsonl"),
            plot=PlotlyChart(kind="table", title="Show outputs"),
        )
    )

    cfg = {'checks': checks, 'log_folder': LOGS_DIR}
    # cfg = Config(checks=checks, settings=Settings(logs_folder=LOGS_DIR))
    return cfg

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

    # start_streamlit()
    # import pdb; pdb.set_trace()

    # JsonWriter(fpath=experiment_path + "/input.jsonl").make_executor().run(input_dataset)
    JsonWriter(fpath=experiment_path + "/input_without_schema.jsonl").make_executor().run(input_dataset)

    # TODO figure out a better way to do this.
    with_schema_dataset_check = SimpleCheck(
        name="get_schema_check",
        compute=[
            GetSchemaDefinition(),
        ],
        source=JsonReader(fpath=experiment_path + "/input_without_schema.jsonl"),
        sink=JsonWriter(fpath=experiment_path + "/input.jsonl"),
    )
    with_schema_dataset_check.make_executor(Settings(logs_folder=experiment_path)).run()

    all_checks = copy.deepcopy(args['evaluation_args']['checks'])

    user_inputs['evaluation_args'] = get_config()
    manager = ExperimentManager(user_inputs)
    manager.run()

    cfg = get_config()
    experiment_path = LOGS_DIR
    all_checks = copy.deepcopy(cfg['checks'])
    for check in all_checks:
        if check.source is not None:
            check.source.fpath = check.source.fpath.format(experiment_path=experiment_path)
        if check.sink is not None:
            check.sink.fpath = check.sink.fpath.format(experiment_path=experiment_path)
    cfg = Config(checks=all_checks, settings=Settings(logs_folder=LOGS_DIR))
    cfg.setup()
    for check in cfg.checks:
        results = check.make_executor(cfg.settings).run()

    if args.start_streamlit:
        start_streamlit()

    # import pdb; pdb.set_trace()