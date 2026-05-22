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


def make_doc(text, source="data/mock.txt", header_2=None):
    metadata = {"source": source}
    if header_2:
        metadata["Header 2"] = header_2
    return SimpleNamespace(page_content=text, metadata=metadata)


def identity_rerank(_question, documents):
    return [1.0] * len(documents)


class ChatbotBehaviorTests(unittest.TestCase):
    def test_greeting_returns_exact_message(self):
        self.assertEqual(ask_question("Hi there"), EXACT_GREETING_RESPONSE)

    @patch("app.chat.chatbot.rerank_pairs", side_effect=identity_rerank)
    @patch("app.chat.chatbot.get_vector_store")
    def test_no_relevant_results_returns_exact_fallback(
        self,
        mock_get_vector_store,
        _mock_rerank,
    ):
        mock_get_vector_store.return_value = FakeVectorStore()

        self.assertEqual(
            ask_question("What is mechanical engineering?"),
            EXACT_FALLBACK_RESPONSE,
        )

    @patch("app.chat.chatbot.rerank_pairs", side_effect=identity_rerank)
    @patch("app.chat.chatbot.get_vector_store")
    def test_unrelated_vector_match_is_ignored(
        self,
        mock_get_vector_store,
        _mock_rerank,
    ):
        unrelated_doc = make_doc("This is about Flutter widgets.")
        mock_get_vector_store.return_value = FakeVectorStore(
            relevance_results=[(unrelated_doc, 0.95)],
        )

        self.assertEqual(
            ask_question("What is mechanical engineering?"),
            EXACT_FALLBACK_RESPONSE,
        )

    @patch("app.chat.chatbot.rerank_pairs", side_effect=identity_rerank)
    @patch("app.chat.chatbot.get_llm")
    @patch("app.chat.chatbot.get_vector_store")
    def test_contents_chunk_is_ignored_when_real_match_exists(
        self,
        mock_get_vector_store,
        mock_get_llm,
        _mock_rerank,
    ):
        contents_doc = make_doc(
            "Contents 1. ListView 2. RecyclerView 3. Intents",
            source="data/android.docx",
        )
        actual_doc = make_doc(
            "RecyclerView Is a more advanced version of ListView with improved performance and other benefits. Recycler View can take position horizontally and vertically.",
            source="data/android.docx",
            header_2="RecyclerView",
        )
        mock_get_vector_store.return_value = FakeVectorStore(
            relevance_results=[(contents_doc, 0.4), (actual_doc, 0.9)],
        )
        fake_llm = FakeLLM("RecyclerView answer")
        mock_get_llm.return_value = fake_llm

        ask_question("RecyclerView")

        self.assertEqual(len(fake_llm.prompts), 1)
        self.assertIn(actual_doc.page_content, fake_llm.prompts[0])
        self.assertNotIn(contents_doc.page_content, fake_llm.prompts[0])

    @patch("app.chat.chatbot.rerank_pairs", side_effect=identity_rerank)
    @patch("app.chat.chatbot.get_llm")
    @patch("app.chat.chatbot.get_vector_store")
    def test_inheritance_match_builds_prompt_from_retrieved_context(
        self,
        mock_get_vector_store,
        mock_get_llm,
        _mock_rerank,
    ):
        inheritance_doc = make_doc(
            "Inheritance: Kisi bhi class ki properties aur methods ko dusri classes ma resuable kernay ka liye use kerty hain.",
            source="data/oop.txt",
        )
        mock_get_vector_store.return_value = FakeVectorStore(
            relevance_results=[(inheritance_doc, 0.8)],
        )
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

    @patch("app.chat.chatbot.rerank_pairs", side_effect=identity_rerank)
    @patch("app.chat.chatbot.get_llm")
    @patch("app.chat.chatbot._get_corpus_terms", return_value=("polymorphism",))
    @patch("app.chat.chatbot.get_vector_store")
    def test_misspelled_query_is_refined_to_matching_knowledge_base_term(
        self,
        mock_get_vector_store,
        _mock_corpus_terms,
        mock_get_llm,
        _mock_rerank,
    ):
        polymorphism_doc = make_doc(
            "Polymorphism: Aik method different action perform ker raha hai.",
            source="data/OOP.docx",
        )
        mock_get_vector_store.return_value = FakeVectorStore(
            relevance_results=[(polymorphism_doc, 0.8)],
        )
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

    @patch("app.chat.chatbot.rerank_pairs", side_effect=identity_rerank)
    @patch("app.chat.chatbot.get_llm")
    @patch("app.chat.chatbot.get_vector_store")
    def test_debouncing_match_builds_prompt_from_retrieved_context(
        self,
        mock_get_vector_store,
        mock_get_llm,
        _mock_rerank,
    ):
        debouncing_doc = make_doc(
            "What is Debouncing?(wait until stop) Use case: Search input optimization.",
            source="data/React Native Notes/React_Native_Interview_Knowledge_Base.md",
            header_2="Debouncing",
        )
        mock_get_vector_store.return_value = FakeVectorStore(
            relevance_results=[(debouncing_doc, 0.85)],
        )
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

    @patch("app.chat.chatbot.rerank_pairs", side_effect=identity_rerank)
    @patch("app.chat.chatbot.get_llm")
    @patch("app.chat.chatbot.get_vector_store")
    def test_fallback_is_returned_exactly_even_if_model_wraps_it(
        self,
        mock_get_vector_store,
        mock_get_llm,
        _mock_rerank,
    ):
        unrelated_doc = make_doc(
            "Kotlin coroutines are used for async work on Android services only.",
            source="data/kotlin.txt",
        )
        mock_get_vector_store.return_value = FakeVectorStore(
            relevance_results=[(unrelated_doc, 0.2)],
        )
        mock_get_llm.return_value = FakeLLM(
            "I am happy to help. Sorry, I don't have this information in my knowledge base."
        )

        response = ask_question("Difference between React and React Native")

        self.assertEqual(response, EXACT_FALLBACK_RESPONSE)

    @patch("app.chat.chatbot.rerank_pairs", side_effect=identity_rerank)
    @patch("app.chat.chatbot.get_llm")
    @patch("app.chat.chatbot.get_vector_store")
    def test_real_life_example_query_prefers_example_heavy_abstraction_chunk(
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
            "Real-Life Analogy: Abstraction -> You just press Withdraw and do not see the backend banking system.",
            source="data/OOP.docx",
        )
        mock_get_vector_store.return_value = FakeVectorStore(
            relevance_results=[(generic_doc, 0.7), (example_doc, 0.6)],
        )
        fake_llm = FakeLLM("Abstraction real-life example answer")
        mock_get_llm.return_value = fake_llm

        ask_question("Any real life example of abstraction?")

        self.assertEqual(len(fake_llm.prompts), 1)
        self.assertLess(
            fake_llm.prompts[0].find(example_doc.page_content),
            fake_llm.prompts[0].find(generic_doc.page_content),
        )

    @patch("app.chat.chatbot.rerank_pairs", side_effect=identity_rerank)
    @patch("app.chat.chatbot.get_llm")
    @patch("app.chat.chatbot.get_vector_store")
    def test_return_sources_includes_metadata(
        self,
        mock_get_vector_store,
        mock_get_llm,
        _mock_rerank,
    ):
        debouncing_doc = make_doc(
            "Debouncing delays execution until inactivity stops.",
            source="data/React Native Notes/React_Native_Interview_Knowledge_Base.md",
            header_2="Debouncing",
        )
        mock_get_vector_store.return_value = FakeVectorStore(
            relevance_results=[(debouncing_doc, 0.9)],
        )
        mock_get_llm.return_value = FakeLLM("Debouncing answer")

        answer, sources = ask_question("debouncing", return_sources=True)

        self.assertEqual(answer, "Debouncing answer")
        self.assertEqual(len(sources), 1)
        self.assertIn("React_Native", sources[0]["source"])
        self.assertEqual(sources[0]["heading"], "Debouncing")


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
