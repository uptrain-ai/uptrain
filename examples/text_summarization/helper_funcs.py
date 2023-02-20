
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
import numpy as np

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
