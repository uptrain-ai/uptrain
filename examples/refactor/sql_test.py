import openai
import copy

from uptrain.framework.config import Config, Settings, SimpleCheck
from uptrain.io import JsonReader
from uptrain.operators import PlotlyChart
from regression_testing.experiment import ExperimentManager
from uptrain.operators.language.sql import HasStar

prompt_template = """
    You are a {persona} whose job is to only output SQL command for a given question. Do not output anything other than the SQL command.
    
    Here is the schema for my database:
    {schema}
    
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
        'file_name': "/Users/bhanu/src/uptrain_experiments/llm/SQL.jsonl",
        'input_variables': ['question', 'schema'],
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
        # sink=JsonWriter(fpath="{experiment_path}/interim_data/has_star.jsonl"),
        plot=PlotlyChart(kind="histogram", title="Distribution of has star", props=dict(x="has_star"))
    ))

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