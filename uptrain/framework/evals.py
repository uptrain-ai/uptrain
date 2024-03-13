import enum
import typing as t

from pydantic import BaseModel, ConfigDict


class Evals(enum.Enum):
    CONTEXT_RELEVANCE = "context_relevance"
    FACTUAL_ACCURACY = "factual_accuracy"
    RESPONSE_RELEVANCE = "response_relevance"
    CRITIQUE_LANGUAGE = "critique_language"
    RESPONSE_COMPLETENESS = "response_completeness"
    RESPONSE_COMPLETENESS_WRT_CONTEXT = "response_completeness_wrt_context"
    RESPONSE_CONSISTENCY = "response_consistency"
    RESPONSE_CONCISENESS = "response_conciseness"
    VALID_RESPONSE = "valid_response"
    RESPONSE_ALIGNMENT_WITH_SCENARIO = "response_alignment_with_scenario"
    RESPONSE_SINCERITY_WITH_SCENARIO = "response_sincerity_with_scenario"
    PROMPT_INJECTION = "prompt_injection"
    CODE_HALLUCINATION = "code_hallucination"
    SUB_QUERY_COMPLETENESS = "sub_query_completeness"
    CONTEXT_RERANKING = "context_reranking"
    CONTEXT_CONCISENESS = "context_conciseness"


class ParametricEval(BaseModel):
    model_config = ConfigDict(protected_namespaces=())


class CritiqueTone(ParametricEval):
    llm_persona: str = "helpful-chatbot"


class GuidelineAdherence(ParametricEval):
    guideline: str
    guideline_name: str = (
        "guideline"  # User-assigned name of the guideline to distinguish between multiple checks
    )
    response_schema: t.Union[str, None] = (
        None  # Schema of the response in case it is of type JSON, XML, etc.
    )


class ConversationSatisfaction(ParametricEval):
    user_persona: str = "user"
    llm_persona: t.Union[str, None] = None


class CustomPromptEval(ParametricEval):
    prompt: str  # Evaluation prompt for the LLM
    choices: list[
        str
    ]  # We only support Grading evals, list of choices for the LLM to select from. ex: [Correct, Incorrect]
    choice_scores: t.Union[
        list[float], list[int]
    ]  # Scores associated for each choice. ex: [1.0, 0.0]
    eval_type: t.Literal["classify", "cot_classify"] = "cot_classify"
    prompt_var_to_column_mapping: t.Union[dict[str, str], None] = (
        None  # Specify matching between variables in the evaluation prompt and keys in your data
    )


class ResponseMatching(ParametricEval):
    method: str = "llm"


class JailbreakDetection(ParametricEval):
    model_purpose: str = (
        "To help the users with their queries without providing them with any illegal, immoral or abusive content."
    )
