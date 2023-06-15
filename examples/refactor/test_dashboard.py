try:
    import plotly
except ImportError:
    raise ImportError("Must have plotly installed to run this example")
from pydantic import BaseModel

import plotly.data
from uptrain.framework import CheckSet, Settings, SimpleCheck
from uptrain.io import JsonReader
from uptrain.operators import PlotlyChart, register_op


LOGS_DIR = "/tmp/uptrain_logs"


def write_data():
    # create some sample data
    data = plotly.data.experiment()
    data.to_json("/tmp/samples.jsonl", orient="records", lines=True)


@register_op
class Noop(BaseModel):
    """A simple operator that does nothing."""

    kind: str = "noop"

    def make_executor(self, settings=None):
        return NoopExecutor(self)


class NoopExecutor:
    op: Noop

    def __init__(self, op):
        self.op = op

    def run(self, data):
        return {"output": data}


def run_as_config():
    # Define the config
    cfg = CheckSet(
        source=JsonReader(fpath="/tmp/samples.jsonl"),
        checks=[
            SimpleCheck(
                name="experiment_data",
                compute=[Noop()],
                plot=PlotlyChart.Histogram(
                    title="Distribution of scores in experiment 1",
                    props=dict(x="experiment_1", nbins=10),
                    filter_on=["gender", "group"],
                ),
            )
        ],
        settings=Settings(logs_folder=LOGS_DIR),
    )

    # Execute the config
    cfg.setup()
    cfg.run()


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
