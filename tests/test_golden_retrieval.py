import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.chat.chatbot import (
    EXACT_FALLBACK_RESPONSE,
    EXACT_GREETING_RESPONSE,
    ask_question,
    retrieve_relevant_documents,
)
from tests.golden_helpers import evaluate_retrieval, load_golden_cases


class FakeVectorStore:
    def __init__(self, relevance_results=None):
        self.relevance_results = relevance_results or []

    def similarity_search_with_relevance_scores(self, question, k, score_threshold):
        return self.relevance_results


def identity_rerank(_question, documents):
    return [1.0] * len(documents)


class GoldenRetrievalTests(unittest.TestCase):
    def test_golden_file_has_expanded_set(self):
        cases = load_golden_cases()
        retrieve_cases = [case for case in cases if case["expect"] == "retrieve"]
        self.assertGreaterEqual(len(cases), 25)
        self.assertGreaterEqual(len(retrieve_cases), 18)

    @patch("app.chat.chatbot.rerank_pairs", side_effect=identity_rerank)
    def test_golden_retrieval_expectations(self, _mock_rerank):
        if not Path("chroma_db").exists():
            self.skipTest("chroma_db missing — run: uv run python -m scripts.ingest")

        failures = []

        for case in load_golden_cases():
            if case["expect"] not in {"retrieve", "fallback"}:
                continue

            if case["expect"] == "fallback":
                with patch("app.chat.chatbot._retrieve_from_vector_store", return_value=[]):
                    error = evaluate_retrieval(case, retrieve_relevant_documents)
            else:
                error = evaluate_retrieval(case, retrieve_relevant_documents)

            if error:
                failures.append(f"{case['id']}: {error}")

        if failures:
            self.fail("\n".join(failures))


class GoldenGreetingTests(unittest.TestCase):
    def test_golden_greeting(self):
        from tests.golden_helpers import evaluate_answer

        for case in load_golden_cases():
            if case["expect"] != "greeting":
                continue
            self.assertIsNone(evaluate_answer(case, ask_question(case["question"])))


class ChromaRetrievalTests(unittest.TestCase):
    @patch("app.chat.chatbot.rerank_pairs", side_effect=identity_rerank)
    def test_unrelated_vector_match_is_filtered_without_lexical_overlap(self, _mock_rerank):
        unrelated_doc = SimpleNamespace(
            page_content="This is about Flutter widgets only.",
            metadata={"source": "data/flutter.md"},
        )

        with patch(
            "app.chat.chatbot._retrieve_from_vector_store",
            return_value=[(unrelated_doc, 0.95)],
        ):
            results = retrieve_relevant_documents("What is mechanical engineering?")

        self.assertEqual(results, [])

    @patch("app.chat.chatbot.rerank_pairs", side_effect=identity_rerank)
    @patch("app.chat.chatbot.get_llm")
    @patch("app.chat.chatbot.get_vector_store")
    def test_fallback_when_retrieval_empty(
        self, mock_get_vector_store, _mock_llm, _mock_rerank
    ):
        mock_get_vector_store.return_value = FakeVectorStore()

        self.assertEqual(
            ask_question("What is mechanical engineering?"),
            EXACT_FALLBACK_RESPONSE,
        )


if __name__ == "__main__":
    unittest.main()
