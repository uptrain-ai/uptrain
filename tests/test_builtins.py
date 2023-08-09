"""
Test that the builtin checks work without raising an error. NOT that they are appropriate for the task.
"""

import polars as pl

from uptrain.framework import CheckSet, Settings
from uptrain.framework.builtins import (
    CheckContextRelevance,
    CheckLanguageQuality,
    CheckResponseCompleteness,
    CheckResponseFacts,
    CheckToneQuality,
    CheckResponseRelevance
)

settings = Settings()
dataset = pl.DataFrame(
    {
        "response": [
            "The actress who played Lolita, Sue Lyon, was 14 at the time of filming.",
            "Shakespeare wrote 154 sonnets.",
            "Sachin Tendulkar retired from cricket in 2013.",
            "Python language was created by Guido van Rossum.",
            "The first manned Apollo mission was Apollo 1.",
        ],
        "question": [
            "What was the age of Sue Lyon when she played Lolita?",
            "How many sonnets did Shakespeare write?",
            "When did Sachin Tendulkar retire from cricket?",
            "Who created the Python language?",
            "Which was the first manned Apollo mission?",
        ],
        "context": [
            "Lolita is a 1962 psychological comedy-drama film directed by Stanley Kubrick. The film follows Humbert Humbert, a middle-aged literature lecturer who becomes infatuated with Dolores Haze, a young adolescent girl. It stars Sue Lyon as the titular character.",
            "William Shakespeare was an English playwright and poet, widely regarded as the world's greatest dramatist. He is often called the Bard of Avon. His works consist of some 39 plays, 154 sonnets and a few other verses.",
            "Sachin Tendulkar is a former international cricketer from India. He is widely regarded as one of the greatest batsmen in the history of cricket. He is the highest run scorer of all time in International cricket and played until 16 May 2013.",
            "Python is a high-level general-purpose programming language. Its design philosophy emphasizes code readability. Its language constructs aim to help programmers write clear, logical code for both small and large-scale projects.",
            "The Apollo program was a human spaceflight program carried out by NASA. It accomplished landing the first humans on the Moon from 1969 to 1972. The program was named after Apollo, the Greek god of light, music, and the sun. The first mission flown was dubbed as Apollo 1.",
        ],
    }
)


def test_check_context_relevance():
    check = CheckContextRelevance()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)


def test_check_language_quality():
    check = CheckLanguageQuality()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)


def test_check_response_completeness():
    check = CheckResponseCompleteness()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)


def test_check_response_relevance():
    check = CheckResponseRelevance()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)


def test_check_response_facts():
    check = CheckResponseFacts()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)


def test_check_tone_quality():
    check = CheckToneQuality(persona="wikipedia-bot")
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
