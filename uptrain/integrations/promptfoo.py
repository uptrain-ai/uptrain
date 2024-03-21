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

    def install(self):
        try:
            subprocess.run(["npm", "install", "promptfoo@" + pr_u.PROMPTFOO_version])
            logger.success("Install Successfully")
        except Exception as e:
            logger.error("Error installing Promptfoo:" + e)
            logger.error("Try running npx promptfoo@" + pr_u.PROMPTFOO_version)

    def evaluate(
        self,
        evals_list: t.Union[list],
        evals_weight: t.Union[list],
        input_data: t.Union[list[dict], pl.DataFrame, pd.DataFrame],
        prompts: t.Union[str],
        providers: t.Union[list],
        threshold: t.Optional[float] = 0.5,
        output_file: t.Optional[str] = "results_" + timestr + ".csv",
        port: t.Optional[int] = pr_u.generate_open_port(),
        eval_model: t.Optional[str] = "gpt-3.5-turbo-1106",
        project_name: t.Optional[str] = "EvalPromptfoo " + str(timestr),
        kill_process_on_exit: t.Optional[bool] = True,
    ) -> None:
        try:
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
                                    input_data[i],
                                    evals_compiled[j],
                                    threshold,
                                    eval_model,
                                    project_name,
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
                    [
                        "npx",
                        "--yes",
                        "promptfoo@" + pr_u.PROMPTFOO_version,
                        "eval",
                        "-o",
                        output_file,
                    ]
                )
                logger.success("Evaluations successfully generated")
                logger.success("Saved results to file: " + output_file)
                try:
                    subprocess.run(
                        [
                            "npx",
                            "promptfoo@" + pr_u.PROMPTFOO_version,
                            "view",
                            "-y",
                            "-p",
                            str(port),
                        ]
                    )
                except Exception as e:
                    logger.error(
                        "Something failed: Try running !npx promptfoo@latest view" + e
                    )

            except Exception as e:
                logger.error(f"Evaluation failed with error: {e}")
                raise e
        except Exception:
            if kill_process_on_exit:
                try:
                    pid = subprocess.check_output(["lsof", "-t", "-i:" + str(port)])
                    pids_str = pid.decode()
                    pids = [
                        int(pid)
                        for pid in pids_str.split("\n")
                        if pid.strip().isdigit()
                    ]
                    try:
                        for pid in pids:
                            subprocess.run(["kill", str(pid)])
                        print(
                            f"Closed application at http://localhost:{port} successfully"
                        )
                        print("To reopen it try running view method in EvalPromptfoo")
                    except subprocess.CalledProcessError:
                        pass
                except Exception:
                    print("No running process to close")
            else:
                return None

    def view(
        self, port: t.Optional[int] = pr_u.generate_open_port(),
        kill_process_on_exit: t.Optional[bool] = True,
        ) -> None:
        try:
            try:
                subprocess.run(
                    [
                        "npx",
                        "promptfoo@" + pr_u.PROMPTFOO_version,
                        "view",
                        "-y",
                        "-p",
                        str(port),
                    ]
                )
            except Exception as e:
                logger.error(
                    "Something failed: Try running !npx promptfoo@latest view" + e
                )
        
        except:
            if kill_process_on_exit:
                try:
                    pid = subprocess.check_output(["lsof", "-t", "-i:" + str(port)])
                    pids_str = pid.decode()
                    pids = [
                        int(pid)
                        for pid in pids_str.split("\n")
                        if pid.strip().isdigit()
                    ]
                    try:
                        for pid in pids:
                            subprocess.run(["kill", str(pid)])
                        print(
                            f"Closed application at http://localhost:{port} successfully"
                        )
                        print(f"To reopen it try running view method in EvalPromptfoo")
                    except subprocess.CalledProcessError as e:
                        pass
                except:
                    print("No running process to close")
            else:
                return None

    def custom(self, command: t.Union[str] = "init"):
        try:
            subprocess.run(["npx", "promptfoo@" + pr_u.PROMPTFOO_version, command])
        except Exception as e:
            logger.error("Something failed: " + e)
