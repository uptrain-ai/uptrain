user_inputs = {
    'experiment_args': {
        "prompt_templates": ["Imagine you are a {persona} who will explain the given concept in 10 words only. Explain {concept}: "],
        "model_names": ["gpt-3.5-turbo"],
        "comparison_args": [{
            "comparison_variables": 'persona',
            'comparison_options': ['school teacher', 'subject matter expert']
            # 'comparison_options': ['school teacher', 'subject matter expert', 'youtube celebrity', 'scientist', 'college professor']
        }],
    },
    'dataset_args': {
        'file_name': "/Users/sourabhagrawal/Desktop/codes/llm/uptrain_experiments/uptrain/concepts.jsonl",
        'input_variables': ['concept', 'feature'],
        'target_variables': ['ideal']
    },
    'evaluation_args': [
        {'type': 'grammar_check', 'of': 'model_output'},  # Implemented by UpTrain 
        {'type': 'semantic_similarity', 'between': ['model_input', 'model_output']},  # Implemented by UpTrain
        {'type': 'model_grading'}  # Implemented by UpTrain 
    ]
}

from regression_testing.experiment import ExperimentManager
from uptrain.io.readers import JsonReader

manager = ExperimentManager(user_inputs['experiment_args'])
reader = JsonReader(
    fpath='/Users/sourabhagrawal/Desktop/codes/llm/uptrain_experiments/uptrain/concepts.jsonl'
)
samples = reader.make_executor().run()
results = manager.run(samples)

results.write_csv("llm_results.csv")
