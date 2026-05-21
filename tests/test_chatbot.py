import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.chat.chatbot import (
    EXACT_FALLBACK_RESPONSE,
    EXACT_GREETING_RESPONSE,
    ask_question,
)
from app.loaders.document_loader import load_documents
from app.utils.preprocess import clean_text


class FakeVectorStore:
    def __init__(self, relevance_results=None):
        self.relevance_results = relevance_results or []

    def similarity_search_with_relevance_scores(self, question, k, score_threshold):
        return self.relevance_results


class FakeLLM:
    def __init__(self, content):
        self.content = content
        self.prompts = []

    def invoke(self, prompt):
        self.prompts.append(prompt)
        return SimpleNamespace(content=self.content)


def make_doc(text, source="data/mock.txt"):
    return SimpleNamespace(page_content=text, metadata={"source": source})


class ChatbotBehaviorTests(unittest.TestCase):
    def test_greeting_returns_exact_message(self):
        self.assertEqual(ask_question("Hi there"), EXACT_GREETING_RESPONSE)

    @patch("app.chat.chatbot._get_local_chunks", return_value=())
    @patch("app.chat.chatbot.get_vector_store")
    def test_no_relevant_results_returns_exact_fallback(
        self,
        mock_get_vector_store,
        _mock_local_chunks,
    ):
        mock_get_vector_store.return_value = FakeVectorStore()

        self.assertEqual(
            ask_question("What is mechanical engineering?"),
            EXACT_FALLBACK_RESPONSE,
        )

    @patch("app.chat.chatbot._get_local_chunks", return_value=())
    @patch("app.chat.chatbot.get_vector_store")
    def test_unrelated_vector_match_is_ignored(
        self,
        mock_get_vector_store,
        _mock_local_chunks,
    ):
        unrelated_doc = make_doc("This is about Flutter widgets.")
        mock_get_vector_store.return_value = FakeVectorStore(
            relevance_results=[(unrelated_doc, 0.95)],
        )

        self.assertEqual(
            ask_question("What is mechanical engineering?"),
            EXACT_FALLBACK_RESPONSE,
        )

    @patch("app.chat.chatbot.get_llm")
    @patch("app.chat.chatbot.get_vector_store")
    @patch("app.chat.chatbot._get_local_chunks")
    def test_contents_chunk_is_ignored_when_real_match_exists(
        self,
        mock_local_chunks,
        mock_get_vector_store,
        mock_get_llm,
    ):
        contents_doc = make_doc(
            "Contents 1. ListView 2. RecyclerView 3. Intents",
            source="data/android.docx",
        )
        actual_doc = make_doc(
            "RecyclerView Is a more advanced version of ListView with improved performance and other benefits. Recycler View can take position horizontally and vertically.",
            source="data/android.docx",
        )
        mock_local_chunks.return_value = (contents_doc, actual_doc)
        mock_get_vector_store.side_effect = RuntimeError("vector store unavailable")
        fake_llm = FakeLLM("RecyclerView answer")
        mock_get_llm.return_value = fake_llm

        ask_question("RecyclerView")

        self.assertEqual(len(fake_llm.prompts), 1)
        self.assertIn(actual_doc.page_content, fake_llm.prompts[0])
        self.assertNotIn(contents_doc.page_content, fake_llm.prompts[0])

    @patch("app.chat.chatbot.get_llm")
    @patch("app.chat.chatbot.get_vector_store")
    @patch("app.chat.chatbot._get_local_chunks")
    def test_local_inheritance_match_builds_prompt_from_retrieved_context(
        self,
        mock_local_chunks,
        mock_get_vector_store,
        mock_get_llm,
    ):
        inheritance_doc = make_doc(
            "Inheritance: Kisi bhi class ki properties aur methods ko dusri classes ma resuable kernay ka liye use kerty hain.",
            source="data/oop.txt",
        )
        mock_local_chunks.return_value = (inheritance_doc,)
        mock_get_vector_store.side_effect = RuntimeError("vector store unavailable")
        fake_llm = FakeLLM(
            "Inheritance means reusing the properties and methods of one class in other classes."
        )
        mock_get_llm.return_value = fake_llm

        response = ask_question("What is inheritance?")

        self.assertEqual(
            response,
            "Inheritance means reusing the properties and methods of one class in other classes.",
        )
        self.assertEqual(len(fake_llm.prompts), 1)
        self.assertIn(inheritance_doc.page_content, fake_llm.prompts[0])
        self.assertIn("What is inheritance?", fake_llm.prompts[0])

    @patch("app.chat.chatbot.get_llm")
    @patch("app.chat.chatbot.get_vector_store")
    @patch("app.chat.chatbot._get_corpus_terms", return_value=("polymorphism",))
    @patch("app.chat.chatbot._get_local_chunks")
    def test_misspelled_query_is_refined_to_matching_knowledge_base_term(
        self,
        mock_local_chunks,
        _mock_corpus_terms,
        mock_get_vector_store,
        mock_get_llm,
    ):
        polymorphism_doc = make_doc(
            "Polymorphism: Aik method different action perform ker raha hai.",
            source="data/OOP.docx",
        )
        mock_local_chunks.return_value = (polymorphism_doc,)
        mock_get_vector_store.side_effect = RuntimeError("vector store unavailable")
        fake_llm = FakeLLM("Polymorphism means one method can perform different actions.")
        mock_get_llm.return_value = fake_llm

        response = ask_question("Polymorphisim")

        self.assertEqual(
            response,
            "Polymorphism means one method can perform different actions.",
        )
        self.assertEqual(len(fake_llm.prompts), 1)
        self.assertIn(polymorphism_doc.page_content, fake_llm.prompts[0])
        self.assertIn("RETRIEVAL QUESTION:\npolymorphism", fake_llm.prompts[0])

    @patch("app.chat.chatbot.get_llm")
    @patch("app.chat.chatbot.get_vector_store")
    @patch("app.chat.chatbot._get_local_chunks")
    def test_local_debouncing_match_builds_prompt_from_retrieved_context(
        self,
        mock_local_chunks,
        mock_get_vector_store,
        mock_get_llm,
    ):
        debouncing_doc = make_doc(
            "What is Debouncing?(wait until stop) Use case: Search input optimization.",
            source="data/React Native Notes/Umair React Native Notes.docx",
        )
        mock_local_chunks.return_value = (debouncing_doc,)
        mock_get_vector_store.side_effect = RuntimeError("vector store unavailable")
        fake_llm = FakeLLM(
            "Debouncing waits until the action stops, and a use case is search input optimization."
        )
        mock_get_llm.return_value = fake_llm

        response = ask_question("debouncing")

        self.assertEqual(
            response,
            "Debouncing waits until the action stops, and a use case is search input optimization.",
        )
        self.assertEqual(len(fake_llm.prompts), 1)
        self.assertIn(debouncing_doc.page_content, fake_llm.prompts[0])
        self.assertIn("debouncing", fake_llm.prompts[0])

    @patch("app.chat.chatbot.get_llm")
    @patch("app.chat.chatbot.get_vector_store")
    @patch("app.chat.chatbot._get_local_chunks")
    def test_fallback_is_returned_exactly_even_if_model_wraps_it(
        self,
        mock_local_chunks,
        mock_get_vector_store,
        mock_get_llm,
    ):
        react_doc = make_doc(
            "Bridging in Flutter is used for bridging native code in flutter side.",
            source="data/flutter.docx",
        )
        mock_local_chunks.return_value = (react_doc,)
        mock_get_vector_store.side_effect = RuntimeError("vector store unavailable")
        mock_get_llm.return_value = FakeLLM(
            "I am happy to help. Sorry, I don't have this information in my knowledge base."
        )

        response = ask_question("Difference between React and React Native")

        self.assertEqual(response, EXACT_FALLBACK_RESPONSE)

    @patch("app.chat.chatbot.get_llm")
    @patch("app.chat.chatbot.get_vector_store")
    @patch("app.chat.chatbot._get_local_chunks")
    def test_real_life_example_query_prefers_example_heavy_abstraction_chunk(
        self,
        mock_local_chunks,
        mock_get_vector_store,
        mock_get_llm,
    ):
        generic_doc = make_doc(
            "Example: introduce an abstraction interface between modules.",
            source="data/solid.txt",
        )
        example_doc = make_doc(
            "Real-Life Analogy: Abstraction -> You just press Withdraw and do not see the backend banking system.",
            source="data/OOP.docx",
        )
        mock_local_chunks.return_value = (generic_doc, example_doc)
        mock_get_vector_store.side_effect = RuntimeError("vector store unavailable")
        fake_llm = FakeLLM("Abstraction real-life example answer")
        mock_get_llm.return_value = fake_llm

        ask_question("Any real life example of abstraction?")

        self.assertEqual(len(fake_llm.prompts), 1)
        self.assertLess(
            fake_llm.prompts[0].find(example_doc.page_content),
            fake_llm.prompts[0].find(generic_doc.page_content),
        )


class DocumentLoaderTests(unittest.TestCase):
    def test_markdown_knowledge_base_is_loaded(self):
        sources = {
            document.metadata.get("source")
            for document in load_documents()
        }

        self.assertIn(
            "data/React Native Notes/React_Native_Interview_Knowledge_Base.md",
            sources,
        )


class PreprocessTests(unittest.TestCase):
    def test_clean_text_preserves_meaningful_line_breaks(self):
        raw_text = "Heading\n\nLine one   with   spaces\nLine two\n\n\nNext section"

        self.assertEqual(
            clean_text(raw_text),
            "Heading\n\nLine one with spaces\nLine two\n\nNext section",
        )


if __name__ == "__main__":
    unittest.main()
