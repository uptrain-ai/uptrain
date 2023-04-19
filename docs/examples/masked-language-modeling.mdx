---
title: Masked Language Modeling
description: Fine-tuning a Large Language Model 
---

**Overview:** In this example, we will see how to fine-tune a large pre-trained language model such as BERT for the task of masked language modelling. Masked language modelling involves masking a certain percentage of tokens or words in a sentence and training the model to predict the masked tokens. Fine-tuning involves further training the pre-trained model on a specific task such as sentiment analysis or question-answering by adjusting the model's parameters to fit the specific task's requirements. We will use UpTrain to filter our dataset to make our data match specific conditions as defined in the problem statement.

**Why is fine-tuning needed:** Pre-trained language models, such as GPT-2 and BERT, are trained on large amounts of text data, which makes them very powerful. However, they are trained on generic tasks and may not be optimized for specific tasks. Fine-tuning the pre-trained model on a specific task, such as sentiment analysis or question-answering, allows the model to adapt to the task's specific requirements, resulting in improved performance. This makes fine-tuning essential to achieve optimal results on a specific NLP task.

**Problem:** In this example, we aim to generate positive sentiment predictions for a given text with masked words such as "Nike shoes are very [MASK]". The challenge is to ensure that the predicted words have a positive connotation, such as "Comfortable", "Durable", or "Good-looking". Conversely, negative sentiment words like "Expensive", "Ugly", or "Dirty" must not be predicted, as they may lead to inaccurate or undesired results. Thus, the goal is to achieve accurate predictions of masked words with a positive sentiment, while avoiding negative sentiment predictions that could affect the overall performance of the model.

**Solution:** We will be using UpTrain framework, which provides an easy-to-use technique for defining customized signals that make the process of data filtering less tedious. Data Integrity checks can also be applied to remove null-valued data. We make use of 🤗 Trainer API to perform fine-tuning on our pretrained model

#### Install Required packages

- [PyTorch](https://pytorch.org/get-started/locally/): Deep learning framework.
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/installation): To use pretrained state-of-the-art models.
- [Hugging Face Datasets](https://pypi.org/project/datasets/): Use public Hugging Face datasets
- [IPywidgets](https://ipywidgets.readthedocs.io/en/stable/user_install.html): For interactive notebook widgets


#### Model and Testing Data Setup

Define few cases to test our model performance before and after retraining.


```python
testing_texts = [
    "Nike shoes are very [MASK]",
    "Nike atheletic wear is known for being very [MASK]",
    "Nike [MASK] shoes are very comfortable",
    "Trousers and Hoodies made by [MASK] are not very expensive",
    "Nike tshirts are famous for being [MASK]"
]
```

Initialize the model and tokenizer from the distilbert-base-uncased model


```python
model, tokenizer = get_model_and_tokenizer(model_checkpoint)
```


Let's visualize the model structure to understand the complexity behind these large language models

Take a look at the outputs of the vanilla distilbert-base-uncased model on predicting the outputs for the masked sentence:

"Nike shoes are very [MASK]"

Notice that we get the output "expensive" among the top 5 predictions. We want to fine-tune the model so that the predicted words form sentences that have a positive sentiment.


```python
original_model_outputs = [top_k_tokens(model, tokenizer, text, k=10) for text in testing_texts]
print('      Text:', testing_texts[0])
print('Top tokens:', original_model_outputs[0])
```

          Text: Nike shoes are very [MASK]
    Top tokens: ['popular', 'durable', 'expensive', 'comfortable', 'fashionable', 'attractive', 'common', 'effective', 'versatile', 'valuable']


#### Dataset Usage/Synthesis

For this task, we can use datasets that are available online, synthesize our own datasets or use a combination of the two. To demonstrate the functionality of UpTrain, synthesizing our own dataset will do.

In the dataset synthesis, we generate two forms of sentences that we want to fine-tune the model on. Refer to the function definition of `create_sample_dataset`. Note that some sentences that will be formed may not make complete sense but that is not very relevant.


```python
SYNTHESIZED_DATASET_SIZE = 25000
uptrain_save_fold_name = "uptrain_smart_data_bert"
synthesized_data_csv = 'data.csv'
synthesized_data_json = 'data.json'

# Create our own dataset of reviews for different companies, products, etc.
dataset = create_sample_dataset(SYNTHESIZED_DATASET_SIZE)
df = pd.DataFrame(dataset['data'])
df.reset_index(drop=True, inplace=True)

df.to_csv(synthesized_data_csv)
create_dataset_from_csv(synthesized_data_csv, 'text', synthesized_data_json)

with open(synthesized_data_json) as file:
    dataset = json.loads(file.read())
```

```
Dataset size: 25000
                                                    text  label
0          tshirts made by under armour offer impressive      1
1             nike gym wear are renowned for being style      1
2         nike gym wear are renowned for being ergonomic      1
3                   converse footballs are revolutionary      1
4      under armour shirts are famous for being inferior      0
...                                                  ...    ...
24995         wristbands made by nike feature durability      1
24996  gym wear made by nike are renowned for being s...      1
24997  trainers made by reebok are recognized for bei...      0
24998  hoodies made by asics are praised for being in...      1
24999              fila sweaters are known for being fit      1

[25000 rows x 2 columns]
```

#### UpTrain Initialization and Retraining Dataset Generation

Define helper functions that UpTrain will use to detect edge cases which the model will fine-tune on instead of using the entire dataset.

- `nike_text_present_func`: Checks for the existence of "nike" in a sentence
- `nike_product_keyword_func`: Checks if the sentence contains a product that is manufactured by Nike
- `is_positive_sentiment_func`: Checks if a sentence has positive sentiment


```python
vader_sia = SentimentIntensityAnalyzer()

def nike_text_present_func (inputs, outputs, gts=None, extra_args={}):
    is_present = []
    for text in inputs["text"]:
        text = text.lower()
        is_present.append(bool("nike" in text))
    return is_present

def nike_product_keyword_func (inputs, outputs, gts=None, extra_args={}):
    is_present = []
    for text in inputs["text"]:
        text = text.lower()
        is_present.append(any(word in text for word in PRODUCTS))
    return is_present

def is_positive_sentiment_func (inputs, outputs, gts=None, extra_args={}):
    is_positive = []
    for text in inputs["text"]:
        text = text.lower()
        if vader_sia.polarity_scores(text)["compound"] < 0:
            is_positive.append(False)
            continue
        is_positive.append(any(word in text for word in POSITIVE_SENTIMENT_ADJECTIVES))
    return is_positive
```

Define the UpTrain Framework configuration


```python
cfg = {
    'checks': [
        {
            "type": uptrain.Monitor.EDGE_CASE,
            "signal_formulae": \
                uptrain.Signal("Is 'Nike' text present?", nike_text_present_func) &
                uptrain.Signal("Is it a Nike product?", nike_product_keyword_func) &
                uptrain.Signal("Is positive sentiment?", is_positive_sentiment_func)
        },

        {
            "type": uptrain.Monitor.DATA_INTEGRITY,
            "measurable_args": {
                "type": uptrain.MeasurableType.INPUT_FEATURE,
                "feature_name": "text"
            },
            "integrity_type": "non_null"
        }
    ],

    # Define where to save the retraining dataset
    "retraining_folder": uptrain_save_fold_name,
    
    # Define when to retrain, define a large number because we
    # are not retraining yet
    "retrain_after": 10000000000,

    "logging_args": {"st_logging": True},
}

dashboard_name = "llm_bert_example"
framework = uptrain.Framework(cfg)
```

Filter out the data that we want to specifically fine-tune on as defined by the configuration provided above


```python
for index, sample in enumerate(dataset['data']):
    if index % 500 == 0:
        print(f'Processed {index} samples')
    inputs = {'text': [sample['text']]}
    framework.log(inputs = inputs, outputs = None)

retraining_csv = uptrain_save_fold_name + '/1/smart_data.csv'
retraining_json = 'retrain_dataset.json'
create_dataset_from_csv(retraining_csv, 'text', retraining_json)
```

```
Processed 24500 samples
8950 edge cases identified out of 24996 total samples
```

#### Finetune the Model


```python
# The number of training epochs is set low here. Higher number of epochs
# result in better performance
trainer, _, _, _ = retrain_model(model, retraining_json, num_train_epochs=2)
```

```
{'eval_loss': 0.664297878742218, 'eval_runtime': 12.8072, 'eval_samples_per_second': 6.481, 'eval_steps_per_second': 0.234, 'epoch': 2.0}
After Training Eval Results:
    {
    "eval_loss": 0.664297878742218,
    "eval_runtime": 12.8072,
    "eval_samples_per_second": 6.481,
    "eval_steps_per_second": 0.234,
    "epoch": 2.0
}
    After Training Perplexity: 1.94
```


```python
retrained_model_outputs = [top_k_tokens(model, tokenizer, text) for text in testing_texts]

for i in range(len(testing_texts)):
    print('                Text:', testing_texts[i])
    print(' Original Top tokens:', original_model_outputs[i][:5])
    print('Retrained Top tokens:', retrained_model_outputs[i][:5])
```

```
                    Text: Nike shoes are very [MASK]
     Original Top tokens: ['popular', 'durable', 'expensive', 'comfortable', 'fashionable']
    Retrained Top tokens: ['durable', 'versatile', 'fashionable', 'efficient', 'comfortable']
                    Text: Nike atheletic wear is known for being very [MASK]
     Original Top tokens: ['durable', 'expensive', 'popular', 'fashionable', 'rare']
    Retrained Top tokens: ['durable', 'fashionable', 'lightweight', 'efficient', 'flexible']
                    Text: Nike [MASK] shoes are very comfortable
     Original Top tokens: ['polo', 'golf', 'swim', 'tennis', 'nike']
    Retrained Top tokens: ['training', 'basketball', 'soccer', 'running', 'football']
                    Text: Trousers and Hoodies made by [MASK] are not very expensive
     Original Top tokens: ['women', 'manufacturers', 'men', 'amateurs', 'slaves']
    Retrained Top tokens: ['nike', 'honda', 'samsung', 'yamaha', 'bmw']
                    Text: Nike tshirts are famous for being [MASK]
     Original Top tokens: ['.', ':', ';', 'colorful', 'unique']
    Retrained Top tokens: ['inexpensive', 'cheap', 'lightweight', 'versatile', 'durable']
```

We can see from the above output that the model is doing much better at predicting masked words that have positive sentiment associated with them.

In the first example, we see that the model no longer predicts masked words such as "expensive" among its top 5 predictions, which is exactly what we want!

An interesting case to look at is the predictions for example 3. We no longer have swim shoes! 😂

## Visualizing Loss, Perplexity and Mask Prediction Confidence

We can create plots for visualizing training/validation loss and perplexity. We can also plot bar charts to visualize the scores of each predicted masked word (higher scores denote higher confidence of the model at respective mask guesses). Here, we plot confidence scores of the Top 10 predictions of the model for each of the chosen testing sentences.


<img src="https://user-images.githubusercontent.com/5287871/222301188-c0cd92e7-6ec2-4a45-9eb8-61dbd8dbcacb.png" width="500"/> 
<img src="https://user-images.githubusercontent.com/5287871/222301571-2a397d39-6259-4a29-b69f-6cd307d3c101.png" width="500"/> 

    

### Predictions for "Nike shoes are very [MASK]."

<img width="600" src="https://user-images.githubusercontent.com/5287871/222301670-d0dbe91e-4113-445a-8bc5-0eff64b29482.png"/>


### Predictions for "Nike athletic wear is know for being very [MASK]."
    
<img width="600" src="https://user-images.githubusercontent.com/5287871/222301697-7ba8f1d5-c0e8-4d6c-8b04-1b50bc06da20.png"/>


### Predictions for "Nike [MASK] shoes are very comfortable."
    
<img width="600" src="https://user-images.githubusercontent.com/5287871/222301717-d08481df-cc58-460d-882e-d13adc885d1d.png"/>


### Predictions for "Trousers and Hoodies made by [MASK] are not very expensive." 
    
<img width="600" src="https://user-images.githubusercontent.com/5287871/222301755-0de5bdb8-5a7e-45c8-a702-93d48f9a90a0.png"/>


### Predictions for "Nike tshirts are famous for being [MASK]." 
    
<img width="600" src="https://user-images.githubusercontent.com/5287871/222301794-2cda6b17-a6c6-452e-ad55-895f732c90b6.png"/>
