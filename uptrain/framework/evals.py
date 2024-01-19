import enum
import pydantic
import typing as t

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
    CODE_IDENTIFICATION = "code_identification"


class ParametricEval(pydantic.BaseModel):
    ...


class CritiqueTone(ParametricEval):
    llm_persona: str = "helpful-chatbot"


class GuidelineAdherence(ParametricEval):
    guideline: str
    guideline_name: str = "guideline"  # User-assigned name of the guideline to distinguish between multiple checks
    response_schema: t.Union[str, None] = None  # Schema of the response in case it is of type JSON, XML, etc.

class ConversationSatisfaction(ParametricEval):
    user_persona: str = "user"
    llm_persona: t.Union[str, None] = None

class CustomPromptEval(ParametricEval):
    choice_strings: dict
    prompt: str
    eval_type: str
    context_vars: t.Union[dict[str, str], None] = None
    
class ResponseMatching(ParametricEval):
    method: str = "llm"
