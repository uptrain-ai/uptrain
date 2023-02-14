import collections
import numpy as np
import torch
import json
import pandas as pd
import random

from transformers import AutoTokenizer, default_data_collator
from model_constants import *

tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

def tokenize_function(examples):
    result = tokenizer(examples["text"])
    if tokenizer.is_fast:
        result["word_ids"] = [result.word_ids(i) for i in range(len(result["input_ids"]))]
    return result

def group_texts(examples):
    # Concatenate all texts
    concatenated_examples = {k: sum(examples[k], []) for k in examples.keys()}
    # Compute length of concatenated texts
    total_length = len(concatenated_examples[list(examples.keys())[0]])
    # We drop the last chunk if it's smaller than chunk_size
    total_length = (total_length // chunk_size) * chunk_size
    # Split by chunks of max_len
    result = {
        k: [t[i : i + chunk_size] for i in range(0, total_length, chunk_size)]
        for k, t in concatenated_examples.items()
    }
    # Create a new labels column
    result["labels"] = result["input_ids"].copy()
    return result

def whole_word_masking_data_collator(features):
    for feature in features:
        word_ids = feature.pop("word_ids")

        # Create a map between words and corresponding token indices
        mapping = collections.defaultdict(list)
        current_word_index = -1
        current_word = None
        for idx, word_id in enumerate(word_ids):
            if word_id is not None:
                if word_id != current_word:
                    current_word = word_id
                    current_word_index += 1
                mapping[current_word_index].append(idx)

        # Randomly mask words
        mask = np.random.binomial(1, wwm_probability, (len(mapping),))
        input_ids = feature["input_ids"]
        labels = feature["labels"]
        new_labels = [-100] * len(labels)
        for word_id in np.where(mask)[0]:
            word_id = word_id.item()
            for idx in mapping[word_id]:
                new_labels[idx] = labels[idx]
                input_ids[idx] = tokenizer.mask_token_id
        feature["labels"] = new_labels
    return default_data_collator(features)

def test_model(model, text):
    inputs = tokenizer(text, return_tensors="pt")
    token_logits = model(**inputs).logits
    # Find the location of [MASK] and extract its logits
    mask_token_index = torch.where(inputs["input_ids"] == tokenizer.mask_token_id)[1]
    mask_token_logits = token_logits[0, mask_token_index, :]
    # Pick the [MASK] candidates with the highest logits
    top_5_tokens = torch.topk(mask_token_logits, 5, dim=1).indices[0].tolist()
    return [tokenizer.decode([token]) for token in top_5_tokens]

def create_sample_dataset(save_file_name):
    data = {
        "version": "0.1.0",
        "source": "sample",
        "url": "self-generated",
        "data": []
    }
    arr = []
    random_words = ["shoes", "jeans", "tshirts", "sweaters", "pants", "hoodies", "socks", "football"]
    for idx in range(1000):
        arr.append({"text": "Sample " + str(100 * idx) + " training sample - Nike " + random.choice(random_words) + " and " + random.choice(random_words), "label": 0})
        arr.append({"text": "Sample " + str(100 * idx) + " training sample - Adidas " + random.choice(random_words) + " and " + random.choice(random_words), "label": 0})
        arr.append({"text": "Sample " + str(100 * idx) + " training sample - Puma " + random.choice(random_words) + " and " + random.choice(random_words), "label": 0})
        arr.append({"text": "Sample " + str(100 * idx) + " training sample - Bata " + random.choice(random_words) + " and " + random.choice(random_words), "label": 0})
    data["data"] = arr

    with open(save_file_name, 'w') as f:
        json.dump(data, f)
    return save_file_name

def create_dataset_from_csv(file_name, col_name, save_file_name, attrs={}):
    data = pd.read_csv(file_name)
    vals = list(data[col_name])
    r_data = []
    for val in vals:
        try:
            val = eval(val)
        except:
            dummy = 1
        r_data.append({'text': str(val), 'label': 0})
    json_data = attrs
    json_data.update({
        "data": r_data
    })
    with open(save_file_name, 'w') as f:
        json.dump(json_data, f)
    return save_file_name