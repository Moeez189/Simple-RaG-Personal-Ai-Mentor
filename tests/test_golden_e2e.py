"""End-to-end golden tests: retrieval + prompt + answer rules (mocked LLM)."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.chat.chatbot import ask_question, retrieve_relevant_documents
from tests.golden_helpers import evaluate_answer, evaluate_retrieval, load_golden_cases
from tests.test_golden_retrieval import FakeVectorStore


class FakeLLM:
    def __init__(self, content: str):
        self.content = content
        self.prompts = []

    def invoke(self, prompt):
        self.prompts.append(prompt)
        return SimpleNamespace(content=self.content)


class GoldenE2ETests(unittest.TestCase):
    @patch("app.chat.chatbot.get_vector_store")
    def test_golden_answer_cases(self, mock_get_vector_store):
        mock_get_vector_store.return_value = FakeVectorStore()
        failures = []

        for case in load_golden_cases():
            if case["expect"] != "answer":
                continue

            mock_response = case.get("mock_llm_response", "")
            with patch("app.chat.chatbot.get_llm") as mock_get_llm:
                mock_get_llm.return_value = FakeLLM(mock_response)
                answer = ask_question(case["question"])

            error = evaluate_answer(case, answer)
            if error:
                failures.append(f"{case['id']}: {error}")

        if failures:
            self.fail("\n".join(failures))

    @patch("app.chat.chatbot.get_vector_store")
    def test_kb_answer_cases_retrieve_context_first(self, mock_get_vector_store):
        mock_get_vector_store.return_value = FakeVectorStore()
        failures = []

        for case in load_golden_cases():
            if case["expect"] != "answer" or case["id"] == "outside_kb_answer":
                continue

            retrieval_case = {**case, "expect": "retrieve"}
            if "context_must_contain" not in retrieval_case:
                retrieval_case["context_must_contain"] = case.get(
                    "answer_must_contain", []
                )

            error = evaluate_retrieval(retrieval_case, retrieve_relevant_documents)
            if error:
                failures.append(f"{case['id']} retrieval: {error}")

        if failures:
            self.fail("\n".join(failures))

    @patch("app.chat.chatbot.get_vector_store")
    def test_answer_prompt_includes_retrieved_context(self, mock_get_vector_store):
        mock_get_vector_store.return_value = FakeVectorStore()
        case = next(
            case for case in load_golden_cases() if case["id"] == "debouncing_answer"
        )
        fake_llm = FakeLLM(case["mock_llm_response"])

        with patch("app.chat.chatbot.get_llm", return_value=fake_llm):
            ask_question(case["question"])

        self.assertEqual(len(fake_llm.prompts), 1)
        self.assertIn("RETRIEVED CONTEXT:", fake_llm.prompts[0])
        self.assertIn("debounc", fake_llm.prompts[0].lower())


if __name__ == "__main__":
    unittest.main()
