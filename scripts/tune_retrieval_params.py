"""Grid-search retrieval thresholds against golden retrieve cases (Chroma required)."""

from __future__ import annotations

import json
from itertools import product
from pathlib import Path

from tests.golden_helpers import evaluate_retrieval, load_golden_cases

GOLDEN_PATH = Path(__file__).resolve().parent.parent / "tests" / "golden_qa.json"


def main() -> int:
    import app.chat.chatbot as chatbot

    cases = [
        case for case in load_golden_cases() if case["expect"] in {"retrieve", "fallback"}
    ]
    thresholds = [0.25, 0.30, 0.35, 0.40, 0.45]
    top_k_values = [3, 5, 7]
    best = None

    print(f"Tuning over {len(cases)} golden cases\n")

    for threshold, top_k in product(thresholds, top_k_values):
        chatbot.VECTOR_RELEVANCE_THRESHOLD = threshold
        chatbot.TOP_K = top_k

        passed = 0
        for case in cases:
            if case["expect"] == "fallback":
                with __import__("unittest.mock", fromlist=["patch"]).patch(
                    "app.chat.chatbot._retrieve_from_vector_store", return_value=[]
                ):
                    error = evaluate_retrieval(case, chatbot.retrieve_relevant_documents)
            else:
                error = evaluate_retrieval(case, chatbot.retrieve_relevant_documents)

            if not error:
                passed += 1

        print(f"threshold={threshold:.2f} top_k={top_k} -> {passed}/{len(cases)} passed")

        if best is None or passed > best["passed"]:
            best = {"threshold": threshold, "top_k": top_k, "passed": passed}

    if best:
        print(
            f"\nRecommended: VECTOR_RELEVANCE_THRESHOLD={best['threshold']}, "
            f"TOP_K={best['top_k']} ({best['passed']}/{len(cases)} passed)"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
