"""
You must have the `dummy_server_openai_eval` running in the background to run this example.
"""

import shutil
from uptrain.framework.config import Config, Settings, SimpleCheck
from uptrain.io import JsonReader
from uptrain.operators import OpenaiEval, PlotlyChart

# -----------------------------------------------------------
# Set up the requirements to run an openai eval
# -----------------------------------------------------------

sample_data = [
    {
        "input": "Last night at the Oscars, Leonardo DiCaprio, Meryl Streep, and Denzel Washington presented awards while Taylor Swift performed her new song.",
        "output": "Leonardo DiCaprio, Meryl Streep, Denzel Washington, Taylor Swift",
    },
    {
        "input": "In the basketball match last night, Michael Jordan and Lebron James showed off their skills.",
        "output": "Michael Jordan, Lebron James",
    },
    {
        "input": "I recently watched The Office, and I must say Steve Carell and Rainn Wilson were fantastic!",
        "output": "Steve Carell, Rainn Wilson",
    },
    {
        "input": "Taylor Swift, Ed Sheeran, and Billy Joel are going to collaborate on a new song.",
        "output": "Taylor Swift, Ed Sheeran, Billy Joel",
    },
    {
        "input": "Did you know that Tom Cruise did his own stunts in Mission Impossible?",
        "output": "Tom Cruise",
    },
]

eval_config = {
    "extract_celebs": {
        "id": "extract_celebs.dev.match-v1",
        "metrics": ["accuracy"],
        "description": "Evaluate if all the celebrities were extracted from the passage",
    },
    "extract_celebs.dev.match-v1": {
        "class": "custom_fns.extract_celebs:Extractor",
        "args": {
            "samples_jsonl": "samples.jsonl",
            "extract_prompt": "List all the celebrities you can find in the following text:",
            "use_local": True,
        },
    },
}

custom_fn = """
import typing as t
import random
import evals
import evals.metrics
import requests


class Extractor(evals.Eval):
    def __init__(
        self, extract_prompt: str, samples_jsonl: str, use_local: bool, **kwargs
    ):
        super().__init__(**kwargs)
        self.extract_prompt = extract_prompt
        self.samples_jsonl = samples_jsonl
        self.use_local = use_local

    def make_openai_friendly(self, input_text: str):
        return [
            {"role": "user", "content": self.extract_prompt + '\\n\\n' + input_text},
        ]

    def run(self, recorder):
        test_data = evals.get_jsonl(self.samples_jsonl)
        if self.use_local:
            test_samples = test_data
        else:
            test_samples = [
                {
                    **d,
                    "input": self.make_openai_friendly(d["input"]),
                }
                for d in test_data
            ]
        self.eval_all_samples(recorder, test_samples)
        return {
            "accuracy": evals.metrics.get_accuracy(recorder.get_events("match")),
        }

    def eval_sample(self, test_sample: t.Any, rng: random.Random):
        prompt = test_sample["input"]
        if self.use_local:
            result = requests.post(
                "http://localhost:8000/completion/",
                json={"input": prompt},
            )
            sampled = result.text
        else:
            result = self.completion_fn(prompt=prompt, max_tokens=25)
            sampled = result.get_completions()[0]

        evals.record_and_check_match(prompt, sampled, expected=test_sample["output"])
"""


def init_bundle():
    """Create an evaluation bundle at the given path. We need both,
    - a custom registry for eval-config/data/completion-fn that we can point openai-eval to
    - a directory with the custom eval function
    """
    import json
    import os
    import uuid
    import yaml
    from pathlib import Path

    path_str = f"/tmp/{uuid.uuid4().hex}"
    root_path = Path(path_str)

    os.makedirs(root_path)
    print("Initializing a custom openai-eval bundle at", root_path)

    data_path = root_path / "extract_celeb_samples.jsonl"
    with open(data_path, "w") as f:
        for d in sample_data:
            f.write(json.dumps(d) + "\n")

    fns_path = root_path / "custom_fns"
    os.makedirs(fns_path)
    Path(fns_path / "__init__.py").touch()
    with open(fns_path / "extract_celebs.py", "w") as f:
        f.write(custom_fn)

    registry_path = root_path / "custom_registry"
    os.makedirs(registry_path)

    os.makedirs(registry_path / "evals")
    with open(registry_path / "evals" / "extract_celebs.yaml", "w") as f:
        yaml.dump(eval_config, f)

    return path_str


# -----------------------------------------------------------
# Run the eval by proxying through Uptrain
# -----------------------------------------------------------

# initialize the custom eval bundle
bundle_path = init_bundle()


def manual_run():
    # Data needs to be passed at runtime if it isn't the one provided in the openai-eval repo
    reader = JsonReader(fpath=f"{bundle_path}/extract_celeb_samples.jsonl")
    samples = reader.make_executor().run()
    assert samples is not None

    eval_op = OpenaiEval(
        bundle_path=bundle_path,
        completion_name="gpt-3.5-turbo",
        eval_name="extract_celebs",
    )

    results = eval_op.make_executor().run(samples["output"])
    print(results)


# -----------------------------------------------------------
# Use Uptrain by writing and executing a config
# -----------------------------------------------------------

LOGS_DIR = "/tmp/uptrain_logs"


def run_as_config():
    # Define the config
    check = SimpleCheck(
        name="openai_eval",
        compute=[
            {
                "output_cols": [],
                "operator": OpenaiEval(
                    bundle_path=bundle_path,
                    completion_name="gpt-3.5-turbo",
                    eval_name="extract_celebs",
                ),
            }
        ],
        source=JsonReader(fpath=f"{bundle_path}/extract_celeb_samples.jsonl"),
        plot=PlotlyChart(kind="table", title="OpenAI Eval Results"),
    )
    cfg = Config(checks=[check], settings=Settings(logs_folder=LOGS_DIR))

    # Execute the config
    cfg.setup()
    for check in cfg.checks:
        results = check.make_executor(cfg.settings).run()


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
    parser.add_argument("--start-streamlit", default=False, action="store_true")
    args = parser.parse_args()

    # manual_run()
    run_as_config()

    # clean up
    shutil.rmtree(bundle_path)

    if args.start_streamlit:
        start_streamlit()
