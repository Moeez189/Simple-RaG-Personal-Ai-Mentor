import json
from pathlib import Path

from app.chat.chatbot import EXACT_FALLBACK_RESPONSE, EXACT_GREETING_RESPONSE

GOLDEN_PATH = Path(__file__).parent / "golden_qa.json"


def load_golden_cases():
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def evaluate_retrieval(case, retrieve_fn) -> str | None:
    question = case["question"]
    history = case.get("history")
    expect = case["expect"]

    if expect in {"greeting", "answer"}:
        return None

    if expect == "fallback":
        results = retrieve_fn(question, history=history)
        if results:
            return f"expected no retrieval, got {len(results)} chunk(s)"
        return None

    if expect == "retrieve":
        results = retrieve_fn(question, history=history)
        if not results:
            return "expected retrieval, got none"

        combined = " ".join(
            document.page_content.lower() for document, _score in results
        )
        for phrase in case.get("context_must_contain", []):
            if phrase.lower() not in combined:
                return f"context missing '{phrase}'"
        return None

    return f"unknown expect type '{expect}'"


def evaluate_answer(case, answer: str) -> str | None:
    expect = case["expect"]

    if expect == "greeting":
        if answer != EXACT_GREETING_RESPONSE:
            return f"expected greeting, got: {answer[:80]}"
        return None

    if expect == "fallback":
        if answer != EXACT_FALLBACK_RESPONSE:
            return f"expected fallback, got: {answer[:120]}"
        return None

    if expect == "answer":
        if answer == EXACT_FALLBACK_RESPONSE and not case.get("mock_llm_response", "").startswith(
            "Sorry"
        ):
            return "expected answer, got fallback"

        answer_lower = answer.lower()
        for phrase in case.get("answer_must_contain", []):
            if phrase.lower() not in answer_lower:
                return f"answer missing '{phrase}'"

        for phrase in case.get("answer_must_not_contain", []):
            if phrase.lower() in answer_lower:
                return f"answer must not contain '{phrase}'"

        mock_response = case.get("mock_llm_response")
        if mock_response and answer != mock_response:
            return "answer does not match mocked LLM output"
        return None

    return f"unknown expect type '{expect}'"
