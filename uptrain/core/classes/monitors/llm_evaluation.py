# Install the following packages:
# pip install uptrain torch transformers nltk datasets py7zr
try:
    import transformers 
    from transformers import AutoTokenizer, AutoModel, AutoModelForSeq2SeqLM
except:
    transformers = None
import torch
import torch.nn.functional as F
import numpy as np

import numpy as np
from uptrain.core.classes.monitors import AbstractMonitor
from uptrain.core.classes.measurables import MeasurableResolver
from uptrain.constants import Monitor, MeasurableType
from uptrain.core.classes.distances import DistanceResolver
from uptrain.constants import Visual
from uptrain.core.lib.helper_funcs import read_json, dependency_required

from typing import Optional, Union, TYPE_CHECKING
if TYPE_CHECKING:
    from uptrain.core.classes.logging.new_log_handler import (
        LogHandler as NewLogHandler,
        LogWriter,
    )
    from uptrain.core.classes.logging.log_handler import LogHandler


# Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[
        0
    ]  # First element of model_output contains all token embeddings
    input_mask_expanded = (
        attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    )
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9
    )


# Function to get bert embeddings from sentences list
def convert_sentence_to_emb(sentences, sentence_emb_model, device):
    # Load model from HuggingFace Hub
    tokenizer = AutoTokenizer.from_pretrained(sentence_emb_model)
    model = AutoModel.from_pretrained(sentence_emb_model).to(device)

    # Tokenize sentences
    encoded_input = tokenizer(
        sentences, padding=True, truncation=True, return_tensors="pt"
    ).to(device)

    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)

    # Perform pooling
    embs = mean_pooling(model_output, encoded_input["attention_mask"])

    # Normalize embeddings
    return np.array(F.normalize(embs, p=2, dim=1).cpu())


def get_summaries(text, tokenizer, model, device, max_new_tokens):
    prefix = "summarize: "
    this_batch = [prefix + doc for doc in text if doc is not None]
    # Text encoder
    input_embs = tokenizer(
        this_batch, truncation=True, padding=True, return_tensors="pt"
    ).input_ids.to(device)

    # Getting output values
    output_embs = model.generate(input_embs, max_new_tokens=max_new_tokens)

    # Text decoder
    summaries = tokenizer.batch_decode(output_embs, skip_special_tokens=True)

    return summaries


@dependency_required(transformers, "transformers")
class LLMEvaluation(AbstractMonitor):
    log_handler: Union["LogHandler", "NewLogHandler"]
    log_writer: Optional["LogWriter"]

    def base_init(self, fw, check):
        self.dashboard_name = "visual"
        self.monitor_type = Monitor.LLM_EVALUATION
        self.embedding_model = check.get('embedding_model', 'sentence-transformers/paraphrase-MiniLM-L6-v2')
        self.distance_types: list = check.get("distance_types", ['cosine_distance'])
        self.dist_classes = [DistanceResolver().resolve(x) for x in self.distance_types]
        self.device = check.get("device","cpu")
        llm_model_args = check["llm_model_args"]
        self.num_tokens = llm_model_args.get("num_tokens", 30)
        model = check.get("model", "yasminesarraj/flan-t5-small-samsum")
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model).to(self.device)

        dim_reduction_dict = {"type": MeasurableType.DIMENSIONALITY_REDUCTION,
                                    "visual_type": Visual.UMAP,
                                    "feature_name": "emb_data",}
        self.dim_reduction_measurable_pred = MeasurableResolver(dim_reduction_dict).resolve(fw)

        # get handles to the log writer object
        if hasattr(self.log_handler, "make_logger"):
            self.log_writer = self.log_handler.make_logger(
                self.dashboard_name, self.monitor_type, fmt="json"
            )
        else:
            self.log_writer = None

    def base_check(self, inputs, outputs=None, gts=None, extra_args={}):
        text = self.measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        summaries = get_summaries(text, self.tokenizer, self.model, self.device, self.num_tokens)
        emb_pred = convert_sentence_to_emb(summaries, self.embedding_model, self.device)
        emb_gt = convert_sentence_to_emb(gts, self.embedding_model, self.device)
        compressed_emb_pred = self.dim_reduction_measurable_pred.compute_and_log({"emb_data": emb_pred}, outputs=None)

        dists = dict(
            zip(
                self.distance_types,
                [x.compute_distance(emb_gt, emb_pred) for x in self.dist_classes],
            )
        )

        this_data = {"umap": compressed_emb_pred}
        this_data.update({"labels": dists})
        hover_dict = {"id": extra_args["id"], "text": text, "summary": summaries, "gt": gts}
        
        # Write a one-line code to unzip hover_dict into a list of dictionaries
        hover_dict = [dict(zip(hover_dict.keys(), t)) for t in zip(*hover_dict.values())]

        this_data.update({"hover_texts": hover_dict})

        if self.log_writer is not None:
            self.log_writer.log(
                {
                    **this_data,
                }
            )
        else:
            self.log_handler.add_histogram(
                "UMAP",
                this_data,
                self.dashboard_name,
             )
        

    def need_ground_truth(self):
        return True