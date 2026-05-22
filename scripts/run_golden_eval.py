"""Run golden Q&A checks: retrieval, fallback, and optional mocked E2E."""

from __future__ import annotations

import argparse
import sys
from types import SimpleNamespace
from unittest.mock import patch

from app.chat.chatbot import ask_question, retrieve_relevant_documents
from tests.golden_helpers import evaluate_answer, evaluate_retrieval, load_golden_cases
from tests.test_golden_retrieval import identity_rerank


class FakeLLM:
    def __init__(self, content: str):
        self.content = content

    def invoke(self, _prompt):
        return SimpleNamespace(content=self.content)


def run_retrieval(cases) -> tuple[int, int, list[str]]:
    passed = 0
    failed = 0
    failures = []

    with patch("app.chat.chatbot.rerank_pairs", side_effect=identity_rerank):
        return _run_retrieval_cases(cases)


def _run_retrieval_cases(cases) -> tuple[int, int, list[str]]:
    passed = 0
    failed = 0
    failures = []

    for case in cases:
        if case["expect"] not in {"retrieve", "fallback"}:
            continue

        if case["expect"] == "fallback":
            with patch("app.chat.chatbot._retrieve_from_vector_store", return_value=[]):
                error = evaluate_retrieval(case, retrieve_relevant_documents)
        else:
            error = evaluate_retrieval(case, retrieve_relevant_documents)

        if error:
            failed += 1
            failures.append(f"{case['id']}: {error}")
            print(f"[fail] {case['id']}: {case['question']} ({error})")
        else:
            passed += 1
            print(f"[pass] {case['id']}: {case['question']}")

    return passed, failed, failures


def run_e2e(cases) -> tuple[int, int, list[str]]:
    with patch("app.chat.chatbot.rerank_pairs", side_effect=identity_rerank):
        return _run_e2e_cases(cases)


def _run_e2e_cases(cases) -> tuple[int, int, list[str]]:
    passed = 0
    failed = 0
    failures = []

    for case in cases:
        if case["expect"] != "answer":
            continue

        mock_response = case.get("mock_llm_response", "")
        with patch("app.chat.chatbot.get_llm") as mock_get_llm:
            mock_get_llm.return_value = FakeLLM(mock_response)
            answer = ask_question(case["question"])

        error = evaluate_answer(case, answer)
        if error:
            failed += 1
            failures.append(f"{case['id']}: {error}")
            print(f"[fail] {case['id']}: {case['question']} ({error})")
        else:
            passed += 1
            print(f"[pass] {case['id']}: {case['question']}")

    return passed, failed, failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Run golden Q&A evaluation")
    parser.add_argument(
        "--e2e",
        action="store_true",
        help="Also run mocked end-to-end answer checks",
    )
    args = parser.parse_args()

    cases = load_golden_cases()
    print(f"Loaded {len(cases)} golden cases\n")

    print("=== Retrieval & fallback ===")
    r_pass, r_fail, _ = run_retrieval(cases)

    e_pass = e_fail = 0
    if args.e2e:
        print("\n=== Mocked E2E answers ===")
        e_pass, e_fail, _ = run_e2e(cases)

    greeting_count = sum(1 for case in cases if case["expect"] == "greeting")
    print(
        f"\nSummary: retrieval {r_pass} passed / {r_fail} failed; "
        f"e2e {e_pass} passed / {e_fail} failed; "
        f"{greeting_count} greeting case(s) in unittest"
    )
    return 1 if (r_fail + e_fail) else 0


if __name__ == "__main__":
    raise SystemExit(main())
