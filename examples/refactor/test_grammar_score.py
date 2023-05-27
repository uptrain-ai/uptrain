"""
To run this example, you must have the `OPENAI_API_KEY` environment variable set.
"""

from uptrain.io.readers import JsonReader
from uptrain.operators.grammar import GrammarScore

# -----------------------------------------------------------
# Set up the dataset first
# -----------------------------------------------------------

sample_data = [
    {
        "prompt_template": "Explain the concept of `{}` in 20 words or less.",
        "concept": "Cars",
        "answer": "Cars, vehicles with wheels, powered by engines. For transportation, they carry people and goods across distances.",
    },
    {
        "prompt_template": "Explain the concept of `{}` in 20 words or less.",
        "concept": "Roads",
        "answer": "Roads be paths made for vehicles. Constructed with like asphalt or concrete, facilitating smooth travel.",
    },
    {
        "prompt_template": "Explain the concept of `{}` in 20 words or less.",
        "concept": "Trees",
        "answer": "Trees, large plants with a stem, called trunk, supporting branches and leaves. They crucial in ecosystems.",
    },
    {
        "prompt_template": "Explain the concept of `{}` in 20 words or less.",
        "concept": "Stars",
        "answer": "Stars is massive glowing gas balls, like our sun. They produce light and heat through nuclear fusion process.",
    },
    {
        "prompt_template": "Explain the concept of `{}` in 20 words or less.",
        "concept": "Rain",
        "answer": "Rain, water falling from sky. It's part of water cycle, happening when clouds getting heavy with moisture.",
    },
    {
        "prompt_template": "In less than 20 words, describe what a `{}` is.",
        "concept": "Birds",
        "answer": "Birds, warm-blooded animals with feathers. They can fly, but some species can't. Eggs they lay for reproduction.",
    },
    {
        "prompt_template": "In less than 20 words, describe what a `{}` is.",
        "concept": "Mountains",
        "answer": "Mountains, large landforms that rise above the surrounding land. Often having steep slopes and high peaks.",
    },
    {
        "prompt_template": "In less than 20 words, describe what a `{}` is.",
        "concept": "Rivers",
        "answer": "Rivers, large natural water bodies flowing towards ocean, sea or another river. Crucial for ecosystem and human civilization.",
    },
    {
        "prompt_template": "In less than 20 words, describe what a `{}` is.",
        "concept": "Clouds",
        "answer": "Clouds, collection of water droplets or ice crystals suspended in atmosphere. They cause precipitation like rain or snow.",
    },
    {
        "prompt_template": "In less than 20 words, describe what a `{}` is.",
        "concept": "Sun",
        "answer": "Sun, star at the center of solar system. Provides light and heat, essential for life on Earth.",
    },
]

with open("/tmp/samples.jsonl", "w") as f:
    import json

    for row in sample_data:
        f.write(json.dumps(row))
        f.write("\n")

# -----------------------------------------------------------
# Uptrain evaluation part
# -----------------------------------------------------------

reader = JsonReader(fpath="/tmp/samples.jsonl")
score_op = GrammarScore(schema_data={"col_text": "answer"})

input_dataset = reader.make_executor().run()
results = score_op.make_executor().run(input_dataset)
print(results)
