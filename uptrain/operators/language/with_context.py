"""
Implement operators to evaluate question-response-context datapoints from a 
retrieval augmented pipeline. 

Questions we want to answer:
- Is the context relevant?
- Is the answer supported by the context?

- context relevance
- prompt an LLM to extract sentences from the context that are relevant. Score based on that. 
- jaccard score and bert score to see how similar paragraphs are. Hmm, why not just count?
"""

from __future__ import annotations
import typing as t

from loguru import logger
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.operators.language.openai_evals import OpenaiEval
from uptrain.operators.language.llm import LLMMulticlient, Payload

CONTEXT_REL_PROMPT_TEMPLATE = """
[Task]: Extract relevant context. 
You are an evidence-driven expert that places high importance on supporting facts and references. You are presented with a question along with some context to answer it, retrieved using a search engine. 
Please identify and return sentences verbatim from the context that are directly relevant to answering the question. If no sentences are relevant, return 'No relevant sentences'. 

Example 1.
[Question]: What is the capital of France?
[Context]: France, in Western Europe, encompasses medieval cities, alpine villages and Mediterranean beaches. Paris, its capital, is famed for its fashion houses, classical art museums including the Louvre and monuments like the Eiffel Tower.
[Relevant]: Paris, its capital, is famed for its fashion houses, classical art museums including the Louvre and monuments like the Eiffel Tower.

Example 2.
[Question]: Who wrote "Pride and Prejudice"?
[Context]: "Pride and Prejudice" is a romantic novel of manners written by Jane Austen in 1813. The novel follows the character development of Elizabeth Bennet, the dynamic protagonist of the book who learns about the repercussions of hasty judgments and comes to appreciate the difference between superficial goodness and actual goodness.
[Relevant]: "Pride and Prejudice" is a romantic novel of manners written by Jane Austen in 1813.

Task data.
[Question]: {question}
[Context]: {context}
[Relevant]: 
"""


@register_op
class ContextRelevanceScore(ColumnOp):
    """
    Grade how relevant the retrieved context was to answering the question. This is done
    by prompting an LLM to extract sentences from the context that it considers relevant.
    """

    col_question: str = "question"
    col_context: str = "context"
    col_out: str = "context_relevance_score"

    def setup(self, settings: Settings):
        self._api_client = LLMMulticlient(settings=settings)
        return self

    def _make_payload(self, id: t.Any, messages: list[dict], context: str) -> Payload:
        return Payload(
            endpoint="chat.completions",
            data={"model": "gpt-3.5-turbo", "messages": messages, "temperature": 0.2},
            metadata={"index": id, "context": context},
        )

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        input_payloads = []
        for _id, row in enumerate(data.rows(named=True)):
            context = row[self.col_context]
            if isinstance(context, list):
                context = ". ".join(context)

            subs = {
                "question": row[self.col_question],
                "context": context,
            }
            prompt_msgs = [
                {"role": "user", "content": CONTEXT_REL_PROMPT_TEMPLATE.format(**subs)}
            ]
            input_payloads.append(self._make_payload(_id, prompt_msgs, context))

        output_payloads = self._api_client.fetch_responses(input_payloads)
        results = []
        for res in output_payloads:
            idx = res.metadata["index"]
            if res.error is not None:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
                results.append((idx, None))
            else:
                try:
                    context = res.metadata["context"]
                    resp_text = res.response["choices"][0]["message"]["content"]
                    if "no relevant sentences" in resp_text.lower():
                        results.append((idx, 0.0))
                    else:
                        # find overlap between context and response
                        resp_sents = [
                            s.strip() for s in resp_text.split(".") if len(s) > 0
                        ]
                        context_sents = [
                            s.strip() for s in context.split(".") if len(s) > 0
                        ]
                        overlap = sum(1 for sent in resp_sents if sent in context_sents)
                        results.append((idx, overlap / len(context_sents)))
                except Exception as e:
                    logger.error(
                        f"Error when processing payload at index {idx}, not API error: {e}"
                    )
                    results.append((idx, None))

        result_scores = pl.Series(
            [val for _, val in sorted(results, key=lambda x: x[0])]
        ).alias(self.col_out)
        return {"output": data.with_columns(result_scores)}


FACT_GENERATE_PROMPT_TEMPLATE = """
Please breakdown the following text into independent facts. A fact is a sentence that is true or can be verified. Facts should not depend on each another and must not convey the same information. Limit to 5 facts in the output.

Example. 
[Text]: The Eiffel Tower, located in Paris, is one of the most visited monuments in the world. It was named after the engineer Gustave Eiffel, whose company designed and built the tower. Constructed from 1887 to 1889, it was initially criticized by some of France's leading artists and intellectuals.
[Facts]: The Eiffel Tower is located in Paris. It is one of the most visited monuments in the world. The Eiffel Tower was named after the engineer Gustave Eiffel. The Eiffel Tower was constructed from 1887 to 1889.

Task. 
[Text]: {text}
[Facts]: 
"""

FACT_EVAL_PROMPT_TEMPLATE = """
Given the context, for each statement in the facts, assess if it is supported by the given context. Write down 'yes' or 'no' for each fact and why. At the end, write down a final result concatenating all the yes/no answers.

Example.
[Context]: The Eiffel Tower, located in Paris, is one of the most visited monuments in the world. It was named after the engineer Gustave Eiffel, whose company designed and built the tower. Constructed from 1887 to 1889, it was initially criticized by some of France's leading artists and intellectuals.
[Facts]: The Eiffel Tower is located in Paris. The Eiffel Tower was constructed in the later 20th century. 
[Answer]: 
1. The Eiffel Tower is located in Paris.
Reason: yes. The context specifies the location of the Eiffel Tower.
2. The Eiffel Tower is the tallest structure in Paris.
Reason: no. The context does not specify the height of the Eiffel Tower.
3. The Eiffel Tower was constructed in the later 20th century.
Reason: no. The context specifies the construction date of the Eiffel Tower.
Final result: yes, no, no.

Task.
[Context]: {context}
[Facts]: {facts}
[Answer]:
"""


def get_sentences(text: str) -> list[str]:
    return [s.strip() for s in text.split(".") if len(s) > 0]


@register_op
class ResponseFactualScore(ColumnOp):
    """
    Grade how factual the generated response was. This is done by prompting an LLM to
    extract all facts from the response and then checking if they are supported by the
    context.

    Reference:
        - `FACTSCORE: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation` (https://arxiv.org/abs/2305.14251)
        - The `Retrieve-LM` variant of their evaluation technique. (https://github.com/shmsw25/FActScore)
    """

    col_question: str = "question"
    col_context: str = "context"
    col_answer: str = "answer"
    col_out: str = "response_factual_score"

    def setup(self, settings: Settings):
        self._api_client = LLMMulticlient(settings=settings)
        return self

    def _make_payload(self, id: t.Any, messages: list[dict]) -> Payload:
        return Payload(
            endpoint="chat.completions",
            data={"model": "gpt-3.5-turbo", "messages": messages, "temperature": 0.2},
            metadata={"index": id},
        )

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        # generate facts from the response
        input_payloads = []
        for _id, row in enumerate(data.rows(named=True)):
            response = row[self.col_answer]
            prompt_msgs = [
                {
                    "role": "user",
                    "content": FACT_GENERATE_PROMPT_TEMPLATE.format(text=response),
                }
            ]
            input_payloads.append(self._make_payload(_id, prompt_msgs))

        output_payloads = self._api_client.fetch_responses(input_payloads)
        results = []
        for res in output_payloads:
            idx = res.metadata["index"]
            if res.error is not None:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
                results.append((idx, None))
            else:
                resp_text = res.response["choices"][0]["message"]["content"]
                resp_facts = [s.strip() for s in resp_text.split(".") if len(s) > 0]
                results.append((idx, resp_facts))
        ser_facts = pl.Series(
            [val for _, val in sorted(results, key=lambda x: x[0])]
        ).alias("facts")

        # evaluate the facts
        input_payloads = []
        results = []  # for rows without any facts, add a null score right away
        for _id, row in enumerate(data.rows(named=True)):
            context = row[self.col_context]
            if isinstance(context, list):
                context = ". ".join(context)
            facts = ". ".join(ser_facts[_id])

            if facts is None or len(facts) == 0:
                results.append((_id, None))
            else:
                prompt_msgs = [
                    {
                        "role": "user",
                        "content": FACT_EVAL_PROMPT_TEMPLATE.format(
                            context=context, facts=facts
                        ),
                    }
                ]
                input_payloads.append(self._make_payload(_id, prompt_msgs))

        output_payloads = self._api_client.fetch_responses(input_payloads)
        for res in output_payloads:
            idx = res.metadata["index"]
            if res.error is not None:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
                results.append((idx, None))
            else:
                resp_text = res.response["choices"][0]["message"]["content"]
                if "final result" not in resp_text:
                    results.append((idx, None))
                else:
                    resp_text = resp_text.split("final result: ")[1]
                    fact_grades = [s.strip() for s in resp_text.strip().split(".")]
                    fact_score = sum(
                        [1 if s == "yes" else 0 for s in fact_grades]
                    ) / len(fact_grades)
                    results.append((idx, fact_score))

        ser_score = pl.Series([val for _, val in sorted(results, key=lambda x: x[0])])
        return {"output": data.with_columns(ser_score.alias(self.col_out))}
