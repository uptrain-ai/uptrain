from uptrain import EvalLLM, Evals, CritiqueTone
import json

OPENAI_API_KEY = "sk-*****************" # <<< REPLACE THIS WITH YOUR ACTUAL OPENAI API KEY

data = [
    {
        "question": "What is ethical hacking?",
        "context": "Ethical hacking, also known as penetration testing, is the practice of authorized hacking to identify vulnerabilities in computer systems, networks, or applications. Ethical hackers use the same methods and tools as malicious hackers but with the permission of the owner to improve security. They report their findings to the organization, which then fixes the vulnerabilities before they can be exploited by others. This practice is crucial for maintaining robust cybersecurity defenses.",
        "response": "Ethical hacking is the practice of authorized hacking to find security vulnerabilities and improve system defenses.",
    },
    {
        "question": "What is the capital of France?",
        "context": "France is a country located in Western Europe. Its capital city is Paris. Paris is known for its art, fashion, gastronomy, and culture. It is home to the Eiffel Tower, the Louvre Museum, and Notre-Dame Cathedral.",
        "response": "The capital of France is Paris.",
    },
    # Edge Case 1: Empty context
    {
        "question": "What is the capital of France?",
        "context": "",
        "response": "The capital of France is Paris.",
    },
    # Edge Case 2: Irrelevant context
    {
        "question": "What is the capital of France?",
        "context": "The sky is blue. The grass is green.",
        "response": "The capital of France is Paris.",
    },
    # Edge Case 3: Empty response
    {
        "question": "What is the capital of France?",
        "context": "France is a country located in Western Europe. Its capital city is Paris.",
        "response": "",
    },
    # Edge Case 4: Wrong information in response
    {
        "question": "What is the capital of France?",
        "context": "France is a country located in Western Europe. Its capital city is Paris.",
        "response": "The capital of France is Berlin.",
    }
]

eval_llm = EvalLLM(openai_api_key=OPENAI_API_KEY)

results = eval_llm.evaluate(
    data=data,
    checks=[
        Evals.CONTEXT_RELEVANCE,
        Evals.FACTUAL_ACCURACY,
        Evals.RESPONSE_RELEVANCE,
        CritiqueTone(llm_persona="teacher"),
    ],
)

print(json.dumps(results, indent=3))