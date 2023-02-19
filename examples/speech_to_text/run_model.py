# %%
# Installation steps: https://huggingface.co/docs/transformers/installation
# Model borrowed from: https://huggingface.co/docs/transformers/model_doc/speech_to_text
# pip install datasets
# https://github.com/google/sentencepiece#installation
# pip install soundfile librosa

# %%
import torch
from transformers import Speech2TextProcessor, Speech2TextForConditionalGeneration, pipeline, AutoTokenizer, AutoModel
from datasets import load_dataset, Audio
import warnings
import pandas as pd
import numpy as np

import uptrain

warnings.simplefilter('ignore')

# %% [markdown]
# ## Define our model, processor and the datasets

# %%
model = Speech2TextForConditionalGeneration.from_pretrained("facebook/s2t-small-librispeech-asr")
transcriber = pipeline("automatic-speech-recognition", model="facebook/s2t-small-librispeech-asr")

# %%
def process_dataset(dataset):
    dataset = dataset.cast_column("audio", Audio(sampling_rate=16000))
    dataset = dataset.shuffle(seed=42)
    return dataset

dataset_ref = process_dataset(load_dataset("PolyAI/minds14", name="en-US", split="train"))
dataset_prod = process_dataset(load_dataset("PolyAI/minds14", name="es-ES", split="train"))

intents = [
    "BUSINESS LOAN",
    "FREEZE",
    "ABROAD",
    "APP ERROR",
    "DIRECT DEBIT",
    "CARD ISSUES",
    "JOINT ACCOUNT",
    "BALANCE",
    "HIGH VALUE PAYMENT",
    "ATM LIMIT",
    "ADDRESS",
    "PAY BILL",
    "CASH DEPOSIT",
    "LATEST TRANSACTIONS"
]
gts = {}
for data_point in dataset_ref:
    gts.update({data_point['path']: intents[data_point['intent_class']]})
for data_point in dataset_prod:
    gts.update({data_point['path']: intents[data_point['intent_class']]})


# %%
transcriber_ref = [{'id': idx, 'text': transcriber(dataset_ref[idx]['audio']['path'])['text']} for idx in range(min(10,len(dataset_ref)))]

# %%
# Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

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
    embs = torch.nn.functional.normalize(embs, p=2, dim=1)
    embs = np.array(embs)
    embs = np.reshape(embs, (embs.shape[0], 16, 24))
    embs = np.mean(embs, axis=2)
    return np.array(embs, dtype=float) 
    

# %%
emb_sentences = convert_sentence_to_emb([x['text'] for x in transcriber_ref])
for idx in range(len(transcriber_ref)):
    transcriber_ref[idx].update({'emb': emb_sentences[idx].tolist()})

# %%
import json
with open("output_ref_dataset.json", "w") as f:
    json.dump(transcriber_ref, f)
    
audio_ref_data = [{'audio_file': x['audio']['path']} for x in dataset_ref]
with open("input_ref_dataset.json", "w") as f:
    json.dump(audio_ref_data, f)
    

# %%
classifier = pipeline("audio-classification", model="stevhliu/my_awesome_minds_model")
# gts = 

def intent_classification_func(inputs, outputs, gts=None, extra_args={}):
    res = []
    for audio_file in inputs['audio_file']:
        # res.append(extra_args['classifier'](audio_file)[0]['label'])
        res.append(extra_args['gts'][audio_file])
        # print(extra_args['classifier'](audio_file))
    return res

cfg = {
    "checks": [{
        'type': uptrain.Anomaly.DATA_DRIFT,
        'reference_dataset': 'output_ref_dataset.json',
        'is_embedding': True,
        "num_buckets": 4,
        "initial_skip": 50,
        "measurable_args": {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'emb'   # Text embeddings of model output
        }
    },
    {
        'type': uptrain.Anomaly.DATA_DRIFT,
        'reference_dataset': 'input_ref_dataset.json',
        'is_embedding': False,
        "initial_skip": 50,
        "measurable_args": {
            'type': uptrain.MeasurableType.CUSTOM,
            'signal_formulae': uptrain.Signal("Intent", intent_classification_func, extra_args = {'classifier': classifier, "gts": gts})
        }
    }],
    
    "st_logging": True
}

framework = uptrain.Framework(cfg_dict=cfg)

# %%
for idx in range(len(dataset_prod)):
    print(idx)
    inputs = {"data": {"audio_file": [dataset_prod[idx]["audio"]["path"]]}}
    
    preds = transcriber(inputs["data"]["audio_file"])
    
    embs = convert_sentence_to_emb([x['text'] for x in preds])
    inputs['data'].update({"emb": embs})

    framework.log(inputs=inputs, outputs=preds)



