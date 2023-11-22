from __future__ import annotations

import argparse
import subprocess
import sys


EXTRA_PACKAGES = {
    "v0": [
        "pandas>=1.0.0",
        "river",
        "scikit-learn>=1.0.0",
        "umap-learn",
        "json-fix>=0.5.0",
        "xgboost",
    ],
    "local-generation": [
        "tqdm>=4.0",
        "aiolimiter>=1.1",
    ],
    "dashboard": [
        "plotly>=5.0.0",
        "streamlit>=1.23",
        "pyarrow>=10.0.0"
    ],
    "selfhosted": [
        "tqdm>=4.0",
        "aiolimiter>=1.1",
        "plotly>=5.0.0",
        "streamlit>=1.23",
        "pyarrow>=10.0.0",
        "river<0.18",
        "scikit-learn>=1.0.0",
        "umap-learn",
        "rouge-score",
        # "sentence-transformers",
        # "InstructorEmbedding",
        "openai==0.28",
        "llama-index>=0.8.0",
        "evals @ git+https://github.com/openai/evals.git@305b237cdb3884c7ddb6a5d12cb184a83551fcba",
        "replicate",
        "litellm<=0.14",
    ],
    # Add packages here
    "full": [
        "tqdm>=4.0",
        "aiolimiter>=1.1",
        "plotly>=5.0.0",
        "streamlit>=1.23",
        "pyarrow>=10.0.0",
        "river<0.18",
        "scikit-learn>=1.0.0",
        "umap-learn",
        "rouge-score",
        "sentence-transformers",
        "InstructorEmbedding",
        "openai==0.28",
        "llama-index>=0.8.0",
        "evals @ git+https://github.com/openai/evals.git@305b237cdb3884c7ddb6a5d12cb184a83551fcba",
        "replicate",
        "litellm<=0.14",
    ],
}


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--feature",
        choices=EXTRA_PACKAGES.keys(),
        required=True,
        help="Install extra packages for using specific features in Uptrain.",
    )
    return parser


def main(argv=None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)

    if args.feature not in EXTRA_PACKAGES:
        print(f"Unknown feature: {args.feature}", file=sys.stderr)
        return 1
    else:
        packages = EXTRA_PACKAGES[args.feature]
        if args.feature == "full":
            # we want to install torch-cpu if we are installing the full feature
            # Nvidia packages blow up the size of the docker image
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "torch",
                    "torchvision",
                    "--index-url",
                    "https://download.pytorch.org/whl/cpu",
                ],
            )
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", *packages],
        )
        return 0
