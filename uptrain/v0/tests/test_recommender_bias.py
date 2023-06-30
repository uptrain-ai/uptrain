import os
from scipy.spatial.distance import cosine
import subprocess
import json

import uptrain.v0 as v0
from gensim.models import Word2Vec


def test_recommender_bias():
    data_file = "sigir_data.json"
    remote_url = "https://oodles-dev-training-data.s3.amazonaws.com/sigir_data.json"
    if not os.path.exists(data_file):
        try:
            # Most Linux distributions have Wget installed by default.
            # Below command is to install wget for MacOS
            wget_installed_ok = subprocess.call("brew install wget", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print("Successfully installed wget")
        except:
            dummy = 1
        try:
            if not os.path.exists("sigir_data.json"):
                file_downloaded_ok = subprocess.call("wget " + remote_url, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                print("Data downloaded")
        except:
            print("Could not load training data")
            print("Please follow following steps to manually download data")
            print("Step 1: Open in browser: https://oodles-dev-training-data.s3.amazonaws.com/sigir_data.json")
            print("Step 2: Download and move the file to example location (i.e. uptrain/examples/3_shopping_cart_recommendation/")
    else:
        print("Data file exists. Skipping download.")


    with open('sigir_data.json') as f:
        data = json.load(f)

    x_train_sku = [[e['product_sku'] for e in s] for s in data['x_train']]
    model = Word2Vec(sentences=x_train_sku, vector_size=48, epochs=15).wv

    def cosine_dist_init(self):
        self.cos_distances = []
        self.model = model

    def cosine_distance_check(self, inputs, outputs, gts=None, extra_args={}):
        for output, gt in zip(outputs, gts):
            if (not output) or (not gt):
                continue
            y_preds = output[0]
            y_gt = gt
            try:
                vector_test = self.model.get_vector(y_gt)
            except:
                vector_test = []
            vector_pred = self.model.get_vector(y_preds)
            if len(vector_pred)>0 and len(vector_test)>0:
                cos_dist = cosine(vector_pred, vector_test)
                self.cos_distances.append(cos_dist)
                self.log_handler.add_histogram('cosine_distance', self.cos_distances, self.dashboard_name)

    x_test = data['x_test']
    y_test = data['y_test']
    inference_batch_size = 10

    def model_predict(model, x_test_batch):
        """
        Implement the model prediction function. 
        
        :model: Word2Vec model learned from user shopping sessions
        :x_test_batch: list of lists, each list being the content of a cart
        
        :return: the predictions returned by the model are the top-K
        items suggested to complete the cart.

        """
        predictions = []
        for _x in x_test_batch:
            key_item = _x[0]['product_sku']
            nn_products = model.most_similar(key_item, topn=10) if key_item in model else None
            if nn_products:
                predictions.append([_[0] for _ in nn_products])
            else:
                predictions.append([])

        return predictions


    cfg = {
        "checks": [
            # Check to monitor the hit-rate of the model 
            # (i.e., if any recommended item was selected)
            {
                'type': v0.Monitor.CONCEPT_DRIFT,
                'algorithm': v0.DataDriftAlgo.DDM,
                'warn_thres': 2,
                'alarm_thres': 3,
                "measurable_args": {
                    'type': v0.MeasurableType.REC_HIT_RATE,
                    },
            },
            # Define a check on popularity bias
            {
                'type': v0.Monitor.POPULARITY_BIAS,
                'algorithm': v0.BiasAlgo.POPULARITY_BIAS,
                'sessions': x_train_sku,   
            },
            # Custom monitor
            {
                'type': v0.Monitor.CUSTOM_MONITOR,
                'initialize_func': cosine_dist_init,
                'check_func': cosine_distance_check,
                'need_gt': True,
                'dashboard_name': 'cosine_distance'
            },
        ], 
        "retraining_folder": 'uptrain_smart_data', 
    }

    framework = v0.Framework(cfg)


    for i in range(int(len(x_test)/inference_batch_size)):
        # Define input in the format understood by the UpTrain framework
        inputs = {"feats": x_test[i*inference_batch_size:(i+1)*inference_batch_size]}
        
        # Do model prediction
        preds = model_predict(model, inputs['feats'])

        # Log input and output to framework
        ids = framework.log(inputs=inputs, outputs=preds)
        
        # Getting ground truth and logging to framework
        y_test_batch = y_test[i*inference_batch_size:(i+1)*inference_batch_size]
        gts = [y[0]['product_sku'] for y in y_test_batch]
        framework.log(identifiers=ids, gts=gts)
        