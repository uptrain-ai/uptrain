## UpTrain Examples

- *Human Orientation Classification*: In this example, we consider a binary classification task of human orientation while exercising. That is, given the location of 17 key-points of the body such as the nose, shoulders, wrist, hips, ankles, etc., the model tries to predict whether the person is in a horizontal or a vertical position. In this task, we have created several jupyter notebook files that somewhat exhaustively demonstrate the features of the UpTrain package. **It's recommended to use this task to get started with UpTrain**.

- *Fraud Detection*: In this example, we monitor the performance of the machine learning model by measuring the [concept drift](https://en.wikipedia.org/wiki/Concept_drift) using the UpTrain package in the [NSL-KDD dataset](https://www.unb.ca/cic/datasets/nsl.html). Specifically, we use two monitors to measure the drift, one is the popular [Drift Detection Method](https://riverml.xyz/dev/api/drift/DDM/) and other is customly defined. 

- *Shopping Cart Recommendation*: In this example, we consider the task of recommending items for purchase to a user. Here, we measure the [popularity bias](https://computersciencewiki.org/index.php/Popularity_bias) in the recommended items. Also, we measure two custom defined metrics:
  - Cosine distance between the embeddings of predicted and bought (that is, ground truth) items
  - Absolute log price ratio between predicted and bought items

- *Ride Time Estimation*: In this example, the task is a regression task that involves predicting the duration of a ride given certain input features. UpTrain is used to apply data integrity checks, filter relevant data, and monitor model performance for this task.

- *Finetuning LLM*: In this example, we take a look at finetuning a large pre-trained language model (such as [BERT](https://huggingface.co/docs/transformers/model_doc/bert)) for the task of [masked language modelling](https://huggingface.co/docs/transformers/main/tasks/masked_language_modeling). This task involves masking a certain percentage of tokens or words in a sentence and training the model to predict the masked tokens. Our aim is to make mask predictions have more positive sentiment in the context of Nike product reviews. We make use of UpTrain to apply data integrity checks, filter relevant data and monitor model performance.

- *Text Summarization*: In this example, we see how to use UpTrain to monitor performance of a text summarization task in NLP. Summarization creates a shorter version of a document or an article that captures all the important information. We will be using a pre-trained text summarization model. We also showcase the UMAP and t-SNE techniques (both of which are [Non-linear Dimensionality Reduction Techniques](https://en.wikipedia.org/wiki/Nonlinear_dimensionality_reduction)) for embedding visualization.
