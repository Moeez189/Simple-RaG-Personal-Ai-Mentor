"""Live golden E2E tests using Ollama. Run only when Ollama is available."""

import os
import unittest

from app.chat.chatbot import EXACT_FALLBACK_RESPONSE, ask_question
from tests.golden_helpers import load_golden_cases

LIVE_ENABLED = os.getenv("OLLAMA_GOLDEN_E2E", "").lower() in {"1", "true", "yes"}


def ollama_available() -> bool:
    try:
        from langchain_ollama import ChatOllama

        llm = ChatOllama(model="llama3:8b", temperature=0)
        llm.invoke("ping")
        return True
    except Exception:
        return False


@unittest.skipUnless(
    LIVE_ENABLED and ollama_available(),
    "Set OLLAMA_GOLDEN_E2E=1 and start Ollama with llama3:8b",
)
class GoldenLiveE2ETests(unittest.TestCase):
    def test_live_kb_questions_return_answers(self):
        live_cases = [
            case
            for case in load_golden_cases()
            if case["id"] in {"debouncing_question", "usestate", "flutter_stateless"}
        ]

        for case in live_cases:
            answer = ask_question(case["question"])
            self.assertNotEqual(
                answer,
                EXACT_FALLBACK_RESPONSE,
                msg=f"{case['id']} returned fallback",
            )
            self.assertTrue(len(answer) > 20, msg=f"{case['id']} answer too short")

    def test_live_out_of_scope_returns_fallback(self):
        answer = ask_question("What is mechanical engineering?")
        self.assertEqual(answer, EXACT_FALLBACK_RESPONSE)


if __name__ == "__main__":
    unittest.main()
