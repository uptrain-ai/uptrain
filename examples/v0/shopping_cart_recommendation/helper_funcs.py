import os
import json
import subprocess

def load_sigir_data(data_file):
    remote_url = "https://oodles-dev-training-data.s3.amazonaws.com/" + data_file
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
    
    return data
    
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
