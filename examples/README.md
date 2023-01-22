## UpTrain -- Examples to get started quickly

In this section, we consider the following 3 tasks:

1. Orientation classification: In this example, we consider a binary classification task of human orientation while exercising. That is, given the location of 17 key-points of the body such as the nose, shoulders, wrist, hips, ankles, etc., the model tries to predict whether the person is in a horizontal or a vertical position. In this task, we have created several jupyter notebook files that somewhat exhaustively demonstrate the features of the UpTrain package. It's recommended to use this task to get started with UpTrain.

2. Cyber-attack classification: In this example, we monitor the performance of the machine learning model by measuring the [concept drift](https://en.wikipedia.org/wiki/Concept_drift) using the UpTrain package in the [NSL-KDD dataset](https://www.unb.ca/cic/datasets/nsl.html). Specifically, we use two monitors to measure the drift, one is the popular [Drift Detection Method](https://riverml.xyz/dev/api/drift/DDM/) and other is customly defined. 

3. Shopping cart recommendation: In this example, we consider the task of recommending items for purchase to a user. Here, we measure the [popularity bias](https://computersciencewiki.org/index.php/Popularity_bias) in the recommended items. Also, we measure two custom defined metrics: 1) cosine distance between the embeddings of predicted and bought (that is, ground truth) items, 2) Absolute log price ratio between predicted and bought items.


