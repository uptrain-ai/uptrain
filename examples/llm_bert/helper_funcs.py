import collections
import numpy as np
import torch
import json
import pandas as pd
import random

from transformers import (
    AutoTokenizer, default_data_collator
)

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

def top_k_tokens (model, tokenizer, text, k = 5):
    inputs = tokenizer(text, return_tensors="pt").to(DEVICE)
    token_logits = model(**inputs).logits
    mask_token_index = torch.where(inputs["input_ids"] == tokenizer.mask_token_id)[1]
    mask_token_logits = token_logits[0, mask_token_index, :]
    top_k_tokens = torch.topk(mask_token_logits, k, dim=1).indices[0].tolist()
    return [tokenizer.decode([token]) for token in top_k_tokens]

def create_sample_dataset(dataset_size):
    data = {
        "version": "0.1.0",
        "source": "sample",
        "url": "self-generated",
        "data": []
    }
    arr = []

    for idx in range(dataset_size):
        company = random.choice(COMPANIES)
        joiner = random.choice(JOINERS)
        product = random.choice(PRODUCTS)
        label = random.choice([0, 1])

        if label == 0:
            adjective = random.choice(NEGATIVE_SENTIMENT_ADJECTIVES)
        else:
            adjective = random.choice(POSITIVE_SENTIMENT_ADJECTIVES)

        # Additional: expand on list of possible sentences or use real-life dataset
        if random.randint(0, 1) == 0:
            sentence = f'{company} {product} {joiner} {adjective}'
        else:
            sentence = f'{product} made by {company} {joiner} {adjective}'
        arr.append({ "text": sentence, "label": label })  
    data["data"] = arr
    return data

def create_dataset_from_csv(file_name, col_name, save_file_name, attrs={}, min_samples=-1):
    data = pd.read_csv(file_name)
    vals = list(data[col_name])
    r_data = []

    for val in vals:
        r_data.append({'text': str(val), 'label': 0})

    json_data = attrs
    json_data.update({
      "data": r_data
    })

    with open(save_file_name, 'w') as f:
        json.dump(json_data, f)
