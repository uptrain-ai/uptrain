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


class ParametricEval(pydantic.BaseModel):
    ...


class CritiqueTone(ParametricEval):
    persona: str = "helpful-chatbot"


class GuidelineAdherence(ParametricEval):
    guideline: str
    guideline_name: str = "guideline"  # User-assigned name of the guideline to distinguish between multiple checks
    response_schema: t.Union[str, None] = None  # Schema of the response in case it is of type JSON, XML, etc.

class ConversationSatisfaction(ParametricEval):
    role: str = "user"

class ResponseMatching(ParametricEval):
    method: str = "llm"
