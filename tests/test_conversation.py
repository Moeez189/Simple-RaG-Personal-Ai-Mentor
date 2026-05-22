import unittest
from unittest.mock import patch

from app.chat.conversation import (
    build_retrieval_query,
    format_conversation_history,
    is_follow_up,
    parse_history,
)
from app.chat.chatbot import ask_question
from tests.test_chatbot import FakeLLM, FakeVectorStore, identity_rerank, make_doc


class ConversationHelpersTests(unittest.TestCase):
    def test_parse_history_supports_tuple_format(self):
        history = [("What is debouncing?", "Debouncing waits until events stop.")]

        self.assertEqual(
            parse_history(history),
            [
                ("user", "What is debouncing?"),
                ("assistant", "Debouncing waits until events stop."),
            ],
        )

    def test_parse_history_supports_message_dict_format(self):
        history = [
            {"role": "user", "content": "What is useState?"},
            {"role": "assistant", "content": "useState stores local state."},
        ]

        self.assertEqual(len(parse_history(history)), 2)

    def test_follow_up_builds_retrieval_query_from_previous_user_turn(self):
        history = [("What is abstraction?", "Abstraction hides implementation details.")]

        query = build_retrieval_query("give me an example", history)

        self.assertEqual(query, "What is abstraction? give me an example")
        self.assertTrue(is_follow_up("give me an example"))

    def test_standalone_question_is_not_expanded(self):
        history = [("What is debouncing?", "Debouncing waits until events stop.")]

        query = build_retrieval_query("What is useState?", history)

        self.assertEqual(query, "What is useState?")

    def test_format_conversation_history_limits_recent_turns(self):
        history = [
            ("Question one", "Answer one"),
            ("Question two", "Answer two"),
            ("Question three", "Answer three"),
        ]

        formatted = format_conversation_history(history, max_turns=1)

        self.assertIn("Question three", formatted)
        self.assertNotIn("Question one", formatted)


class ConversationChatTests(unittest.TestCase):
    @patch("app.chat.chatbot.rerank_pairs", side_effect=identity_rerank)
    @patch("app.chat.chatbot.get_llm")
    @patch("app.chat.chatbot.get_vector_store")
    def test_follow_up_uses_history_in_prompt_and_retrieval(
        self,
        mock_get_vector_store,
        mock_get_llm,
        _mock_rerank,
    ):
        generic_doc = make_doc(
            "Example: introduce an abstraction interface between modules.",
            source="data/solid.txt",
        )
        example_doc = make_doc(
            "Real-Life Analogy: Abstraction -> You press Withdraw without seeing the backend banking system.",
            source="data/OOP.docx",
        )
        mock_get_vector_store.return_value = FakeVectorStore(
            relevance_results=[(generic_doc, 0.6), (example_doc, 0.55)],
        )
        fake_llm = FakeLLM("Abstraction example answer")
        mock_get_llm.return_value = fake_llm

        history = [("What is abstraction?", "Abstraction hides unnecessary details.")]
        ask_question("Any real life example?", history=history)

        prompt = fake_llm.prompts[0]
        self.assertIn("RECENT CONVERSATION:", prompt)
        self.assertIn("What is abstraction?", prompt)
        self.assertIn("RETRIEVAL QUESTION:", prompt)
        self.assertIn("abstraction", prompt.lower())
        self.assertLess(prompt.find(example_doc.page_content), prompt.find(generic_doc.page_content))


if __name__ == "__main__":
    unittest.main()
