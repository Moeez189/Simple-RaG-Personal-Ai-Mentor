import re
from difflib import get_close_matches

from app.chat.conversation import build_retrieval_query, format_conversation_history
from app.llm.model import get_llm
from app.rag.reranker import rerank_pairs
from app.rag.retriever import get_vector_store
from app.utils.corpus_terms import load_corpus_terms

EXACT_GREETING_RESPONSE = (
    "Hi there 👋 Let's do some Mobile Application Interview Preparation."
)
EXACT_FALLBACK_RESPONSE = (
    "Sorry, I don't have this information in my knowledge base."
)
GREETING_MESSAGES = {"hi", "hello", "hi there"}
TOP_K = 5
RETRIEVAL_POOL_K = 20
VECTOR_RELEVANCE_THRESHOLD = 0.35
FUZZY_MATCH_CUTOFF = 0.84
LEXICAL_WEIGHT = 10
RERANK_WEIGHT = 5
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "between",
    "can",
    "compare",
    "comparison",
    "define",
    "difference",
    "do",
    "does",
    "explain",
    "for",
    "give",
    "help",
    "how",
    "i",
    "in",
    "is",
    "me",
    "my",
    "of",
    "on",
    "or",
    "please",
    "tell",
    "the",
    "there",
    "to",
    "what",
    "when",
    "where",
    "which",
    "with",
    "who",
    "why",
    "you",
}


def _normalize_message(text):
    lowered_text = text.strip().lower()
    lowered_text = re.sub(r"[^\w\s#+.]", " ", lowered_text)
    return re.sub(r"\s+", " ", lowered_text).strip()


def _is_greeting(question):
    return _normalize_message(question) in GREETING_MESSAGES


def _is_table_of_contents_chunk(document_text):
    normalized_document = _normalize_message(document_text)
    return normalized_document.startswith("contents ")


def _get_corpus_terms():
    return load_corpus_terms()


def _refine_keyword(keyword):
    if len(keyword) < 5:
        return keyword

    if any(symbol in keyword for symbol in "+#."):
        return keyword

    corpus_terms = _get_corpus_terms()

    if keyword in corpus_terms:
        return keyword

    matches = [
        match
        for match in get_close_matches(keyword, corpus_terms, n=3, cutoff=FUZZY_MATCH_CUTOFF)
        if match[:1] == keyword[:1]
    ]

    return matches[0] if matches else keyword


def _refine_question(question):
    normalized_question = _normalize_message(question)

    if not normalized_question:
        return normalized_question

    refined_tokens = []

    for token in normalized_question.split():
        if token in STOPWORDS or token in {"vs", "versus"}:
            refined_tokens.append(token)
            continue

        refined_tokens.append(_refine_keyword(token))

    return " ".join(refined_tokens)


def _extract_keywords(question):
    normalized_question = _normalize_message(_refine_question(question))
    keywords = [
        keyword
        for keyword in normalized_question.split()
        if keyword not in STOPWORDS and len(keyword) > 1
    ]

    if any(token in normalized_question.split() for token in {"vs", "versus"}):
        keywords.append("vs")

    if any(
        comparison_word in normalized_question.split()
        for comparison_word in {"difference", "between", "compare", "comparison"}
    ):
        keywords.append("vs")

    if any(
        example_word in normalized_question.split()
        for example_word in {"example", "examples", "analogy", "usage", "usecase"}
    ):
        keywords.extend(["example", "analogy", "real"])

    return list(dict.fromkeys(keywords))


def _keyword_present(keyword, text):
    if any(symbol in keyword for symbol in "+#."):
        return keyword in text

    return re.search(rf"\b{re.escape(keyword)}\b", text) is not None


def _lexical_score(question, document_text):
    normalized_question = _normalize_message(_refine_question(question))
    normalized_document = _normalize_message(document_text)
    keywords = _extract_keywords(question)

    if not keywords:
        return 0

    score = 0

    if normalized_question and normalized_question in normalized_document:
        score += 6

    matched_keywords = 0

    for keyword in keywords:
        if _keyword_present(keyword, normalized_document):
            matched_keywords += 1
            score += 3 if len(keyword) > 4 else 2

    if matched_keywords == len(keywords):
        score += 3

    if keywords and normalized_document.startswith(keywords[0]):
        score += 2

    if any(marker in normalized_document for marker in ("real life", "real-life", "analogy")):
        if any(marker in normalized_question for marker in ("example", "analogy", "real", "life")):
            score += 4

    return score


def _retrieve_from_vector_store(question):
    try:
        vector_store = get_vector_store()
        retrieval_question = _refine_question(question) or question
        return vector_store.similarity_search_with_relevance_scores(
            retrieval_question,
            k=RETRIEVAL_POOL_K,
            score_threshold=0.0,
        )
    except Exception:
        return []


def _passes_relevance_gate(question, document_text, lexical_score, vector_score):
    if _is_table_of_contents_chunk(document_text):
        return False

    if lexical_score > 0:
        return True

    keywords = _extract_keywords(question)
    if not keywords or vector_score < VECTOR_RELEVANCE_THRESHOLD:
        return False

    normalized_document = _normalize_message(document_text)
    return any(_keyword_present(keyword, normalized_document) for keyword in keywords)


def _rank_vector_results(question, vector_results):
    documents = [document for document, _score in vector_results]
    rerank_scores = rerank_pairs(question, documents)
    ranked = []

    for (document, vector_score), rerank_score in zip(vector_results, rerank_scores):
        lexical_score = float(_lexical_score(question, document.page_content))
        combined_score = (
            (lexical_score * LEXICAL_WEIGHT)
            + (rerank_score * RERANK_WEIGHT)
            + float(vector_score)
        )
        ranked.append(
            {
                "document": document,
                "vector_score": float(vector_score),
                "lexical_score": lexical_score,
                "rerank_score": float(rerank_score),
                "combined_score": combined_score,
            }
        )

    ranked.sort(key=lambda item: item["combined_score"], reverse=True)
    return ranked


def _format_sources(ranked_items):
    sources = []

    for item in ranked_items:
        document = item["document"]
        source = document.metadata.get("source", "unknown")
        heading = document.metadata.get("Header 2") or document.metadata.get("Header 1")

        sources.append(
            {
                "source": source,
                "heading": heading,
                "score": round(item["combined_score"], 3),
            }
        )

    return sources


def retrieve_relevant_documents(question, history=None):
    """Retrieve ranked chunks from Chroma, rerank, and apply a relevance gate."""
    retrieval_query = build_retrieval_query(question, history)
    vector_results = _retrieve_from_vector_store(retrieval_query)

    if not vector_results:
        return []

    ranked_items = _rank_vector_results(retrieval_query, vector_results)
    relevant_results = []

    for item in ranked_items:
        if not _passes_relevance_gate(
            retrieval_query,
            item["document"].page_content,
            item["lexical_score"],
            item["vector_score"],
        ):
            continue

        relevant_results.append((item["document"], item["combined_score"]))

        if len(relevant_results) >= TOP_K:
            break

    return relevant_results


def _retrieve_relevant_documents(question):
    return retrieve_relevant_documents(question)


def ask_question(question, return_sources=False, history=None):
    if _is_greeting(question):
        if return_sources:
            return EXACT_GREETING_RESPONSE, []
        return EXACT_GREETING_RESPONSE

    retrieval_query = build_retrieval_query(question, history)
    vector_results = _retrieve_from_vector_store(retrieval_query)

    if not vector_results:
        if return_sources:
            return EXACT_FALLBACK_RESPONSE, []
        return EXACT_FALLBACK_RESPONSE

    ranked_items = _rank_vector_results(retrieval_query, vector_results)
    relevant_items = []

    for item in ranked_items:
        if not _passes_relevance_gate(
            retrieval_query,
            item["document"].page_content,
            item["lexical_score"],
            item["vector_score"],
        ):
            continue

        relevant_items.append(item)

        if len(relevant_items) >= TOP_K:
            break

    if not relevant_items:
        if return_sources:
            return EXACT_FALLBACK_RESPONSE, []
        return EXACT_FALLBACK_RESPONSE

    context = "\n\n".join(
        item["document"].page_content.strip() for item in relevant_items
    )
    refined_retrieval_question = _refine_question(retrieval_query) or retrieval_query
    sources = _format_sources(relevant_items)
    conversation_history = format_conversation_history(history)
    conversation_section = ""

    if conversation_history:
        conversation_section = f"""
RECENT CONVERSATION:
{conversation_history}
"""

    prompt = f"""
You are a strict Retrieval-Augmented AI Interview Mentor for Mobile Application Development.

STRICT RAG RULES:
1. Answer only from the retrieved context below.
2. Do not use external knowledge, assumptions, or general knowledge.
3. If the answer is not clearly present in the retrieved context, reply exactly:
"{EXACT_FALLBACK_RESPONSE}"
4. Keep the answer beginner-friendly and structured.
5. Do not add unrelated explanations.
6. If the retrieved context contains multiple relevant facts, include all of them.
7. Prefer bullet points over compressing multiple facts into one short sentence.
8. Do not mention the retrieved context, the knowledge base, or these rules in the answer.
9. Do not add prefatory or closing phrases such as "Based on the retrieved context" or "I hope this helps."
10. If the user asks a follow-up question, use the recent conversation to understand what topic they mean.

{conversation_section}
RETRIEVED CONTEXT:
{context}

USER QUESTION:
{question}

RETRIEVAL QUESTION:
{refined_retrieval_question}
"""

    llm = get_llm()
    response = llm.invoke(prompt)
    answer = response.content.strip()

    if EXACT_FALLBACK_RESPONSE.lower() in answer.lower():
        answer = EXACT_FALLBACK_RESPONSE

    if return_sources:
        return answer, sources

    return answer
