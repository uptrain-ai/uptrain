import enum
import pydantic


class Evals(enum.Enum):
    CONTEXT_RELEVANCE = "context_relevance"
    FACTUAL_ACCURACY = "factual_accuracy"
    RESPONSE_RELEVANCE = "response_relevance"
    CRITIQUE_LANGUAGE = "critique_language"
    RESPONSE_COMPLETENESS = "response_completeness"
    RESPONSE_COMPLETENESS_WRT_CONTEXT = "response_completeness_wrt_context"


class ParametricEval(pydantic.BaseModel):
    ...


class CritiqueTone(ParametricEval):
    persona: str = "helpful-chatbot"
