import os
import pickle
import collections
from scipy.spatial.distance import cosine
import numpy as np

from reclist.datasets import CoveoDataset
from reclist.recommenders.prod2vec import CoveoP2VRecModel
from reclist.reclist import CoveoCartRecList

import uptrain

coveo_dataset = CoveoDataset()

if not os.path.exists("model_shopping_cart.pickle"):
    model = CoveoP2VRecModel()
    model.train(coveo_dataset.x_train)
    with open("model_shopping_cart.pickle", "wb") as handle:
        pickle.dump(model, handle, protocol=pickle.HIGHEST_PROTOCOL)
else:
    with open("model_shopping_cart.pickle", "rb") as handle:
        model = pickle.load(handle)

rec_list = CoveoCartRecList(model=model, dataset=coveo_dataset)

x_train = coveo_dataset._x_train
x_train_sku = rec_list.sku_only(x_train)
x_test = rec_list._x_test
y_test = rec_list._y_test

# estimate popularity from training data
pop_map = collections.defaultdict(lambda: 0)
num_interactions = 0
for session in x_train_sku:
    for event in session:
        pop_map[event] += 1
        num_interactions += 1

# normalize popularity
pop_map = {k: v / num_interactions for k, v in pop_map.items()}

"""
Measuring cosine distance between the ground 
truth and first predicted item.
"""


def cosine_dist_init(self):
    self.cos_distances = []
    self.model = model


def cosine_distance_check(self, inputs, outputs, gts=None, extra_args={}):
    y_preds = outputs[0]
    y_gt = gts[0]
    if (not y_gt) or (not y_preds):
        return
    vector_test = self.model.get_vector(y_gt[0]["product_sku"])
    vector_pred = self.model.get_vector(y_preds[0]["product_sku"])
    if vector_pred and vector_test:
        cos_dist = cosine(vector_pred, vector_test)
        self.cos_distances.append(cos_dist)
        self.log_handler.add_histogram("cosine_distance", self.cos_distances)


def price_homogeneity_init(self):
    self.price_diff = []
    self.product_data = rec_list.product_data
    self.price_sel_fn = (
        lambda x: float(x["price_bucket"]) if x["price_bucket"] else None
    )


def price_homogeneity_check(self, inputs, outputs, gts=None, extra_args={}):
    y_preds = outputs[0]
    y_gt = gts[0]
    if (not y_gt) or (not y_preds):
        return
    prod_test = self.product_data[y_gt[0]["product_sku"]]
    prod_pred = self.product_data[y_preds[0]["product_sku"]]
    if self.price_sel_fn(prod_test) and self.price_sel_fn(prod_pred):
        test_item_price = self.price_sel_fn(prod_test)
        pred_item_price = self.price_sel_fn(prod_pred)
        abs_log_price_diff = np.abs(np.log10(pred_item_price / test_item_price))
        self.price_diff.append(abs_log_price_diff)
        self.log_handler.add_histogram("price_homogeneity", self.price_diff)


inference_batch_size = len(x_test)
cfg = {
    # Define your metrics to identify data drifts
    "checks": [
        {
            "type": uptrain.Anomaly.POPULARITY_BIAS,
            "algorithm": uptrain.BiasAlgo.POPULARITY_BIAS,
            "rec_list": rec_list,
            "pop_map": pop_map,
        },
        {
            "type": uptrain.Anomaly.CUSTOM_MONITOR,
            "initialize_func": cosine_dist_init,
            "check_func": cosine_distance_check,
            "need_gt": True,
            "dashboard_name": "cosine_distance",
        },
        {
            "type": uptrain.Anomaly.CUSTOM_MONITOR,
            "initialize_func": price_homogeneity_init,
            "check_func": price_homogeneity_check,
            "need_gt": True,
            "dashboard_name": "price_homogeneity",
        },
    ],
    "training_args": {
        "fold_name": "uptrain_smart_data",
        "log_folder": "uptrain_logs",
    },
}


def test_recommendation():
    framework = uptrain.Framework(cfg)

    for i in range(int(len(x_test) / inference_batch_size)):
        inputs = {
            "data": {
                "feats": x_test[
                    i * inference_batch_size : (i + 1) * inference_batch_size
                ]
            }
        }
        y_pred = model.predict(inputs["data"]["feats"])

        idens = framework.log(inputs=inputs, outputs=y_pred)
        framework.log(
            gts=y_test[i * inference_batch_size : (i + 1) * inference_batch_size],
            identifiers=idens,
        )
