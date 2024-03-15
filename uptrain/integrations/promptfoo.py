from __future__ import annotations
from loguru import logger
import polars as pl
import pandas as pd
import typing as t
import subprocess
import time
from uptrain.integrations import promptfoo_utils as pr_u

timestr = time.strftime("%m_%d_%Y-%H:%M:%S")  # used for filename

__all__ = ["EvalPromptfoo"]


class EvalPromptfoo:
    def __init__(self) -> None:
        return None

    def evaluate(
        self,
        evals_list: t.Union[list],
        evals_weight: t.Union[list],
        input_data: t.Union[list[dict], pl.DataFrame, pd.DataFrame],
        threshold: t.Union[float],
        prompts: t.Union[str],
        providers: t.Union[list],
        redirect_webview: t.Optional[bool] = False,
        output_file: t.Optional[str] = "results_" + timestr + ".csv",
        port: t.Optional[int] = pr_u.generate_open_port(),
        eval_model: t.Optional[str] = "gpt-3.5-turbo-1106",
        project_name: t.Optional[str] = "EvalPromptfoo Results  " + timestr
    ):
        evals_compiled = pr_u.compile_evals(evals_list, evals_weight)

        if isinstance(input_data, pl.DataFrame):
            input_data = input_data.to_dicts()
        elif isinstance(input_data, pd.DataFrame):
            input_data = input_data.to_dict(orient="records")

        yaml_data = {
            "prompts": prompts,
            "providers": providers,
            "tests": [
                {
                    "description": "Data " + str(i + 1),
                    "vars": {
                        "question": input_data[i]["question"],
                        "context": input_data[i]["context"],
                    },
                    "threshold": threshold,
                    "assert": [
                        {
                            "type": "python",
                            "value": pr_u.format_uptrain_template(
                                input_data[i], evals_compiled[j], threshold, eval_model, project_name
                            ),
                        }
                        for j in range(len(evals_compiled))
                    ],
                }
                for i in range(len(input_data))
            ],
        }

        pr_u.generate_promptfoo_yaml_file(yaml_data)
        try:
            subprocess.run(
                ["npx", "--yes", "promptfoo@latest", "eval", "-o", output_file]
            )
            logger.success("Evaluations successfully generated")
            logger.success("Saved results to file: " + output_file)
            if redirect_webview:
                try:
                    if isinstance(port, int):
                        subprocess.run(
                            ["npx", "promptfoo@latest", "view", "-y", "-p", str(port)]
                        )
                        logger.success(
                            "Successfully rerouted to promptfoo dashboards @ http://localhost:"
                            + str(port)
                            + "/"
                        )
                    else:
                        subprocess.run(["npx", "promptfoo@latest", "view", "-y"])
                        logger.success(
                            "Successfully rerouted to promptfoo dashboards @ http://localhost:"
                            + str(pr_u.DEFAULT_PORT_PROMPTFOO)
                        )
                except Exception as e:
                    logger.error(f"Failed to generate a view: {e}")
            else:
                try:
                    if isinstance(port, int):
                        subprocess.run(
                            ["npx", "promptfoo@latest", "view", "-p", str(port)]
                        )
                        logger.success(
                            "Open "
                            + str(port)
                            + "/"
                            + " in webbrowser to view dashboards"
                        )
                    else:
                        subprocess.run(["npx", "promptfoo@latest", "view"])
                        logger.success(
                            "Open http://localhost:"
                            + str(pr_u.DEFAULT_PORT_PROMPTFOO)
                            + "/"
                            + " in webbrowser to view dashboards"
                        )
                except Exception as e:
                    logger.error(f"Failed to generate a view: {e}")
        except Exception as e:
            logger.error(f"Evaluation failed with error: {e}")
            raise e
        return None
