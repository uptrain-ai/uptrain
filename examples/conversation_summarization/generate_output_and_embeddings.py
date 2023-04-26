# Install the following packages:
# pip install uptrain torch transformers nltk datasets py7zr

from transformers import AutoTokenizer, AutoModel
from datasets import concatenate_datasets
import torch
import torch.nn.functional as F
import numpy as np
import json
import os
import uptrain
import subprocess
from transformers import pipeline
from datasets import load_dataset

# Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


# Function to get bert embeddings from sentences list
def convert_sentence_to_emb(sentences, device):
    # Load model from HuggingFace Hub
    tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
    model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2').to(device)

    # Tokenize sentences
    encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt').to(device)

    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)

    # Perform pooling
    embs = mean_pooling(model_output, encoded_input['attention_mask'])

    # Normalize embeddings
    return np.array(F.normalize(embs, p=2, dim=1).cpu())

data_dir = 'data'
os.makedirs(data_dir, exist_ok=True)

samsum_dataset = load_dataset("samsum")
dialogsum_dataset = load_dataset("knkarthick/dialogsum")

if torch.cuda.is_available():
    device = 'cuda'
else:
    device = 'cpu'

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer = AutoTokenizer.from_pretrained("lidiya/bart-large-xsum-samsum")
model = AutoModelForSeq2SeqLM.from_pretrained("lidiya/bart-large-xsum-samsum").to(device)

def get_summary_and_embs(tokenizer, model, text, device, max_new_tokens=20):
    prefix = "summarize: "
    this_batch = [prefix + doc for doc in text if doc is not None]
    # Text encoder
    input_embs = tokenizer(this_batch, truncation=True, padding=True, return_tensors="pt").input_ids.to(device)

    # Getting output values
    output_embs = model.generate(input_embs, max_new_tokens=max_new_tokens)

    # Text decoder
    summaries = tokenizer.batch_decode(output_embs, skip_special_tokens=True)
    bert_embs = convert_sentence_to_emb(summaries, device)
    return summaries, output_embs.cpu().numpy(), bert_embs

from functools import reduce
from operator import concat

def generate_data(dataset_name, d_type, batch_size=25): 
    if dataset_name=='dialogsum':
        dataset = dialogsum_dataset[d_type]
    elif dataset_name=='samsum':
        dataset = samsum_dataset[d_type]
    else:
        raise Exception("Dataset Error")
    num_points = len(dataset)

    batch_size = 50
    all_summaries = []
    all_enc_embs = []
    all_bert_embs = []
    for idx in range(int(num_points/batch_size)):
        this_batch = dataset['dialogue'][idx*batch_size: (idx+1)*batch_size]
        summaries, enc_embs, bert_embs = get_summary_and_embs(tokenizer, model, this_batch, device)

        all_summaries.append(summaries)

        all_enc_embs.append(enc_embs)
        all_bert_embs.append(bert_embs)
        if (idx+1) % 10 == 0:
            print("Num predictions logged:", (idx+1)*batch_size)

    all_summaries = reduce(concat, all_summaries)
    file_name = os.path.join(data_dir, f"out_{d_type}_{dataset_name}_summaries.json")
    with open(file_name, "w") as f:
        json.dump(all_summaries, f, cls=uptrain.UpTrainEncoder)

    all_enc_embs = reduce(concat, all_enc_embs)
    file_name = os.path.join(data_dir, f"out_{d_type}_{dataset_name}_enc_embs.json")
    with open(file_name, "w") as f:
        json.dump(all_enc_embs, f, cls=uptrain.UpTrainEncoder)

    all_bert_embs = reduce(concat, all_bert_embs)
    file_name = os.path.join(data_dir, f"out_{d_type}_{dataset_name}_bert_embs.json")
    with open(file_name, "w") as f:
        json.dump(all_bert_embs, f, cls=uptrain.UpTrainEncoder)


# Generate the dataset for three cases:
# samsum train, samsum test and dialogsum train
generate_data('samsum', 'train')
generate_data('samsum', 'test')
generate_data('dialogsum', 'train')



