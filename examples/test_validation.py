import os
os.environ['OPENAI_API_KEY'] = "..."

from uptrain.framework import SimpleCheck, Signal
from uptrain.operators import (
    SelectOp,
)
from uptrain.operators.language import (
    TextComparison,
)
from validation_wrapper import ValidationManager
import openai
import polars as pl


def get_check():
    # Define the check
    check = SimpleCheck(
            name="quality_scores",
            sequence=[
                SelectOp(
                    columns={
                        "is_empty_response": TextComparison(
                            reference_text="<EMPTY MESSAGE>",
                            col_in_text="response",
                        ),
                    }
                )
            ],
        )

    return check


if __name__ == "__main__":

    check = get_check()

    prompt_template = """
        You are a {persona} that can only quote text from documents. You will be given a section of technical documentation titled {document_title}, found at {document_link}. 
        The input is: '{question}?'. The input is a question, a problem statement, or a task. It is about one or many topics. 
        
        You are only allowed to quote sections of text.  
        
        Your task is to quote exactly all sections of the document that are relevant to any topics of the input. If there are code or examples, you must copy those sections too. Copy the text exactly as found in the original document. If you are copying a table, make sure you copy the table headers.
        
        Okay, here is the document:
        --- START: Document ---
        
        # Document title: {document_title}
        {document_text}

        -- END: Document ---
        Now do the task. You are only allowed to quote from the document. If there are no relevant sections, just respond with \"<EMPTY MESSAGE>\".
        
        DO NOT ATTEMPT TO ANSWER THE QUESTION OR PROBLEM. ONLY COPY. ONLY QUOTE.
        Here are the exact sections from the document:
    """

    def get_model_response(input_dictn):
        prompt = [{"role": "system", "content": prompt_template.format(**input_dictn)}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt,
            temperature=0.1
        )
        message = response.choices[0]['message']['content']
        return message

    validation_manager = ValidationManager(
        check=check,
        completion_fn=get_model_response,
        pass_condition=~Signal('is_empty_response')
    )
    validation_manager.setup()

    input_dataset = pl.read_ndjson("examples/datasets/qna_on_docs_samples.jsonl").to_dicts()

    for inputs in input_dataset:
        response = validation_manager.run(inputs)
