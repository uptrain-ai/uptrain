import math

from datasets import load_dataset
from transformers import (
    AutoModelForMaskedLM, AutoTokenizer,
    DataCollatorForLanguageModeling,
    TrainingArguments, Trainer
)

from helper_funcs import *
from model_constants import *


tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)


def get_model_and_tokenizer (model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForMaskedLM.from_pretrained(model_name)

    print('Is "cuda" available?', torch.cuda.is_available())
    if torch.cuda.is_available():
        print('Device:', torch.cuda.get_device_name(0))

    # Assign to suppress output
    _ = model.to(DEVICE)
    return model, tokenizer

def retrain_model(model, dataset, num_train_epochs=num_train_epochs, model_save_file_name=model_save_file_name):
    retrain_dataset = load_dataset('json', data_files={"train": dataset}, field='data')
    tokenized_datasets = retrain_dataset.map(
        tokenize_function, batched=True, remove_columns=["text", "label"]
    )
    lm_datasets = tokenized_datasets.map(group_texts, batched=True)
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm_probability=mlm_probability)
    downsampled_dataset = lm_datasets["train"].train_test_split(
        train_size=train_size, test_size=test_size, seed=42
    )

    # logging_steps = len(downsampled_dataset["train"]) // batch_size
    logging_steps = 5
    eval_steps = 5
    save_steps = 25
    model_name = model_checkpoint.split("/")[-1]

    training_args = TrainingArguments(
        output_dir=model_save_file_name,
        overwrite_output_dir=True,
        logging_strategy="steps",
        evaluation_strategy="steps",
        learning_rate=1e-4,
        weight_decay=0.01,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        logging_steps=logging_steps,
        eval_steps=eval_steps,
        save_steps=save_steps,
        num_train_epochs=num_train_epochs
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=downsampled_dataset["train"],
        eval_dataset=downsampled_dataset["test"],
        data_collator=data_collator,
        tokenizer=tokenizer,
    )

    before_eval_results = trainer.evaluate()
    print('Before Training Eval Results:\n', json.dumps(before_eval_results, indent = 2))
    print(f"  Before Training Perplexity: {math.exp(before_eval_results['eval_loss']):.2f}")

    trainer_results = trainer.train()
    trainer.save_model(model_save_file_name)

    after_eval_results = trainer.evaluate()
    print('After Training Eval Results:\n', json.dumps(after_eval_results, indent = 2))
    print(f"  After Training Perplexity: {math.exp(after_eval_results['eval_loss']):.2f}")

    return (trainer, before_eval_results, after_eval_results, trainer_results)
