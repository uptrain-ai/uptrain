import math

from datasets import load_dataset
from transformers import AutoTokenizer, DataCollatorForLanguageModeling, TrainingArguments, Trainer
from helper_funcs import *
from model_constants import *

tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

def retrain_model(model, dataset):
    retrain_dataset = load_dataset('json', data_files={"train": dataset}, field='data')
    tokenized_datasets = retrain_dataset.map(
        tokenize_function, batched=True, remove_columns=["text", "label"]
    )

    lm_datasets = tokenized_datasets.map(group_texts, batched=True)
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm_probability=mlm_probability)

    downsampled_dataset = lm_datasets["train"].train_test_split(
        train_size=train_size, test_size=test_size, seed=42
    )

    logging_steps = len(downsampled_dataset["train"]) // batch_size
    model_name = model_checkpoint.split("/")[-1]

    training_args = TrainingArguments(
        output_dir=f"{model_name}-finetuned-uptrain",
        overwrite_output_dir=True,
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        weight_decay=0.01,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        logging_steps=logging_steps,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=downsampled_dataset["train"],
        eval_dataset=downsampled_dataset["test"],
        data_collator=data_collator,
        tokenizer=tokenizer,
    )

    eval_results = trainer.evaluate()
    print(f">>>Before training, Perplexity: {math.exp(eval_results['eval_loss']):.2f}")

    trainer.train()

    eval_results = trainer.evaluate()
    print(f">>>After training, Perplexity: {math.exp(eval_results['eval_loss']):.2f}")