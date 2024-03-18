from loguru import logger
import inspect
import yaml
from uptrain import Evals
import socket

DEFAULT_PORT_PROMPTFOO = 15500
PROMPTFOO_version = "latest"
"""
evals: [Evals.Metric1, Evals.Metric2]
weight: [Weight1, Weight2]

Basically weights help to generate weighted average of the metrics we are using

func(compile_evals): we are creating a list which looks like:
[
    {
        'eval_type': Evals.Metri1,
        'eval_weight': Weight1,
        'score_type':  score_metric1,
        'explanation_type':  explanation_metric1
    }
]
"""


def compile_evals(evals, weight):
    if len(evals) != len(weight):
        logger.error("Length of evals != Length of weight")
    if not all(isinstance(_, Evals) for _ in evals):
        logger.error("Please check the list of evals")
    res_dict = [
        {
            "eval_type": str(evals[i]),
            "eval_weight": weight[i],
            "score_type": "score_" + evals[i].value,
            "explanation_type": "explanation_" + evals[i].value,
        }
        for i in range(len(evals))
    ]
    return res_dict


"""
func(tempalate_uptrain_eval):
In itself this function may not look like a function.
Basically, it's more of a template.
We will be using the information inside this function to create yaml file for promptfoo (through inspect)
"""


def tempalate_uptrain_eval():
    from uptrain import EvalLLM, Settings, Evals
    import os

    data = [{"question": input_question, "context": input_context, "response": output}]
    settings = Settings(openai_api_key=os.environ["OPENAI_API_KEY"], model=eval_model)
    eval_llm = EvalLLM(settings=settings)
    results = eval_llm.evaluate(
        project_name=(project_name), data=data, checks=eval_type
    )
    if results[0][score_var] > threshold_var:
        return {
            "pass": True,
            "score": results[0][score_var],
            "reason": results[0][explanation_var],
        }
    else:
        return {
            "pass": False,
            "score": results[0][score_var],
            "reason": results[0][explanation_var],
        }


"""
func(format_uptrain_template): Adds individual variables to the template
"""


def format_uptrain_template(data, evals_compiled, threshold, eval_model, project_name):
    uptrain_template_lines = inspect.getsourcelines(tempalate_uptrain_eval)[0]
    uptrain_template = "".join(uptrain_template_lines[1:])

    uptrain_template = uptrain_template.replace(
        "input_question", "'{}'".format(data["question"])
    )
    uptrain_template = uptrain_template.replace(
        "input_context", "'{}'".format(data["context"])
    )
    uptrain_template = uptrain_template.replace(
        "eval_type", "[{}]".format(evals_compiled["eval_type"])
    )
    uptrain_template = uptrain_template.replace(
        "score_var", "'{}'".format(evals_compiled["score_type"])
    )
    uptrain_template = uptrain_template.replace(
        "explanation_var", "'{}'".format(evals_compiled["explanation_type"])
    )
    uptrain_template = uptrain_template.replace("threshold_var", "{}".format(threshold))
    uptrain_template = uptrain_template.replace("eval_model", "'{}'".format(eval_model))
    uptrain_template = uptrain_template.replace(
        "(project_name)",
        "'{}'".format(project_name + "(" + evals_compiled["eval_type"] + ")"),
    )
    return uptrain_template


"""
Generate yaml file for promptfoo
"""


def generate_promptfoo_yaml_file(py_obj):
    try:
        with open("promptfooconfig.yaml", "w") as f:
            yaml.dump(py_obj, f, sort_keys=False)
    except:
        logger.error("Unable to generate file: promptfooconfig.yaml")


"""
Used to check for an open port
"""


def generate_open_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = DEFAULT_PORT_PROMPTFOO
    port_res = sock.connect_ex(
        ("localhost", DEFAULT_PORT_PROMPTFOO)
    )  # if 0 then default: DEFAULT_PORT_PROMPTFOO already in use

    while port_res == 0 and port > 0:
        port = port - 1
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_res = sock.connect_ex(("localhost", port))

    if port_res == 0:
        sock = socket.socket()
        sock.bind(("", 0))
        port = sock.getsockname()[1]
    return port
