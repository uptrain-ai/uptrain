try:
    import plotly
except ImportError:
    raise ImportError("Must have plotly installed to run this example")

import plotly.data
from uptrain.framework.config import Config, Settings, SimpleCheck
from uptrain.io import JsonReader
from uptrain.operators import GrammarScore, PlotlyChart


LOGS_DIR = "/tmp/uptrain_logs"


def write_data():
    # create some sample data
    data = plotly.data.experiment()
    data.to_json("/tmp/samples.jsonl", orient="records", lines=True)


def run_as_config():
    # Define the config
    check = SimpleCheck(
        name="experiment_data",
        compute=[],
        source=JsonReader(fpath="/tmp/samples.jsonl"),
        plot=PlotlyChart(
            kind="histogram",
            title="Distribution of scores in experiment 1",
            props=dict(x="experiment_1", nbins=10),
            filter_on=["gender", "group"],
        ),
    )
    cfg = Config(checks=[check], settings=Settings(logs_folder=LOGS_DIR))

    # Execute the config
    cfg.setup()
    for check in cfg.checks:
        results = check.make_executor(cfg.settings).run()


def start_streamlit():
    from uptrain.dashboard import StreamlitRunner

    runner = StreamlitRunner(LOGS_DIR)
    runner.start()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--start-streamlit", default=False, action="store_true")
    args = parser.parse_args()

    write_data()
    run_as_config()
    if args.start_streamlit:
        start_streamlit()
