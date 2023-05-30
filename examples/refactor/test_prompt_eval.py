from uptrain.io.readers import JsonReader

reader = JsonReader(
    fpath="/Users/sourabhagrawal/Desktop/codes/llm/uptrain_experiments/uptrain/concepts.jsonl"
)

samples = reader.make_executor().run()

from uptrain.operators.language.openai_evals import PromptEval

eval_op = PromptEval(
    prompt_template="Imagine you are a school teacher who will explain the given concept in 10 words only. Explain {concept}: ",
    prompt_variables=["concept"],
    gt_variables=[],
    model_name="gpt-3.5-turbo",
)

results = eval_op.make_executor().run(samples)
results
