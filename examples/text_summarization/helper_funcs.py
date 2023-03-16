
from transformers import AutoTokenizer, AutoModel
from datasets import concatenate_datasets
import torch
import torch.nn.functional as F
import numpy as np
import json
import os
import uptrain
import subprocess


# Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


# Function to get bert embeddings from sentences list
def convert_sentence_to_emb(sentences):
    # Load model from HuggingFace Hub
    tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
    model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

    # Tokenize sentences
    encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)

    # Perform pooling
    embs = mean_pooling(model_output, encoded_input['attention_mask'])

    # Normalize embeddings
    return np.array(F.normalize(embs, p=2, dim=1))


def downsample_embs(embs, algo='avg'):
    if algo == 'avg':
        embs = np.reshape(embs, (embs.shape[0], 16, -1))
        embs = np.mean(embs, axis=2)
    else:
        raise Exception("algo is not defined")
    return embs


def generate_reference_dataset_with_embeddings(dataset, tokenizer, model, dataset_label="billsum_train"):
    # ref_dataset = billsum['train']
    data = []
    file_name = "ref_dataset.json"
    if not os.path.exists(file_name):
        for jdx in range(10):
            this_batch = ["summarize: " + x for x in dataset["text"][jdx*100: (jdx+1)*100]]
            input_embs = tokenizer(this_batch, truncation=True, padding=True, return_tensors="pt").input_ids
            output_embs = model.generate(input_embs)
            summaries = tokenizer.batch_decode(output_embs, skip_special_tokens=True)
            bert_embs = convert_sentence_to_emb(summaries)
            print("Generated bert embeddings for " + str((jdx+1) * 100) + " training samples")
            bert_embs_downsampled = downsample_embs(bert_embs)
            for idx in range(len(this_batch)):
                data.append({
                    'id': jdx*100+idx,
                    "dataset_label": dataset_label,
                    'title': dataset['title'][jdx*100+idx],
                    'text': dataset['text'][jdx*100+idx],
                    'output': summaries[idx],
                    'bert_embs': bert_embs[idx].tolist(),
                    'bert_embs_downsampled': bert_embs_downsampled[idx].tolist(),
                    'num_words': get_num_words_in_text(dataset[jdx*100+idx], None)
                })

        with open(file_name, "w") as f:
            json.dump(data, f, cls=uptrain.UpTrainEncoder)
    else:
        print("Embeddings for reference dataset exists. Skipping generating again.")
            
        
def combine_datasets(dataset_1, label_1, dataset_2, label_2):
    final_test_dataset = concatenate_datasets([dataset_1, dataset_2])
    label_bill = [label_1 for _ in dataset_1]
    label_wiki = [label_2 for _ in dataset_2]
    labels = label_bill + label_wiki
    final_test_dataset = final_test_dataset.add_column("dataset_label", labels)
    return final_test_dataset

def download_wikihow_csv_file(file_name):
    remote_url = "https://oodles-dev-training-data.s3.us-west-1.amazonaws.com/" + file_name
    if not os.path.exists(file_name):
        print("Starting to download " + file_name)
        try:
            # Most Linux distributions have Wget installed by default.
            # Below command is to install wget for MacOS
            wget_installed_ok = subprocess.call("brew install wget", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print("Successfully installed wget")
        except:
            dummy = 1
        try:
            if not os.path.exists(file_name):
                file_downloaded_ok = subprocess.call("wget " + remote_url, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                print("Data downloaded")
            print("Prepared Wikihow Dataset")
        except Exception as e:
            print(e)
            print("Could not load training data")
            print("Please follow following steps to manually download data")
            print("Step 1: Paste the link https://oodles-dev-training-data.s3.amazonaws.com/wikihowAll.csv in your browser")
            print("Step 2: Once the csv file is downloaded, move it here (i.e. YOUR_LOC/uptrain/examples/text_summarization/")
    else:
        print(file_name + " already present")

def get_num_words_in_text(inputs, outputs, gts=None, extra_args={}):
    txt_buckets = []
    buckets = extra_args.get('buckets', [0, 200, 500, 750, 1000, 2000, 5000, 100000, 100000000])
    for txt in inputs['text']:
        num_words = len(txt.split())
        for idx in range(len(buckets)):
            if (num_words >= buckets[idx]) and (num_words < buckets[idx+1]):
                txt_buckets.append(str(buckets[idx]) + "-" + str(buckets[idx+1]))
                break
    return txt_buckets


def get_num_prepositions_in_text(inputs, outputs, gts=None, extra_args={}):
    num_prepositions = []
    preposition_list = ['in', 'on', 'at', 'among', 'between', 'through', 'across', 'above', 'over', 'up', 'down', 'to', 'with', 'by', 'beside', 'beneath', 'in front of']
    for txt in inputs['text']:
        all_words = txt.split()
        num_prepositions.append(len(list(set(all_words).intersection(preposition_list))))
    return num_prepositions