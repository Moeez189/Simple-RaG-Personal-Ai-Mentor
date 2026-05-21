import re
from difflib import get_close_matches
from functools import lru_cache
from pathlib import Path

from app.llm.model import get_llm
from app.loaders.document_loader import load_documents
from app.rag.retriever import get_vector_store
from app.rag.text_splitter import split_documents

EXACT_GREETING_RESPONSE = (
    "Hi there 👋 Let's do some Mobile Application Interview Preparation."
)
EXACT_FALLBACK_RESPONSE = (
    "Sorry, I don't have this information in my knowledge base."
)
GREETING_MESSAGES = {"hi", "hello", "hi there"}
TOP_K = 5
VECTOR_RELEVANCE_THRESHOLD = 0.45
SUPPORTED_DATA_SUFFIXES = {".txt", ".md", ".pdf", ".docx"}
FUZZY_MATCH_CUTOFF = 0.84
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


@lru_cache(maxsize=4)
def _get_cached_corpus_terms(_data_signature):
    terms = set()

    for document in _get_cached_local_chunks(_data_signature):
        if _is_table_of_contents_chunk(document.page_content):
            continue

        for term in re.findall(r"[a-z0-9#+.]+", _normalize_message(document.page_content)):
            if len(term) > 3:
                terms.add(term)

    return tuple(sorted(terms))


def _get_corpus_terms():
    return _get_cached_corpus_terms(_get_data_signature())


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

    return score


def _get_data_signature():
    signature = []

    for path in sorted(Path("data").rglob("*")):
        if not path.is_file():
            continue

        if path.suffix.lower() not in SUPPORTED_DATA_SUFFIXES:
            continue

        stat = path.stat()
        signature.append((str(path), stat.st_mtime_ns, stat.st_size))

    return tuple(signature)


@lru_cache(maxsize=4)
def _get_cached_local_chunks(_data_signature):
    return tuple(split_documents(load_documents()))


def _get_local_chunks():
    return _get_cached_local_chunks(_get_data_signature())


def _retrieve_from_local_chunks(question):
    scored_results = []

    for document in _get_local_chunks():
        if _is_table_of_contents_chunk(document.page_content):
            continue

        score = _lexical_score(question, document.page_content)

        if score > 0:
            scored_results.append((document, float(score)))

    scored_results.sort(key=lambda item: item[1], reverse=True)
    return scored_results[:TOP_K]


def _retrieve_from_vector_store(question):
    try:
        vector_store = get_vector_store()
        retrieval_question = _refine_question(question) or question
        return vector_store.similarity_search_with_relevance_scores(
            retrieval_question,
            k=TOP_K,
            score_threshold=VECTOR_RELEVANCE_THRESHOLD,
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


def _merge_results(question, lexical_results, vector_results):
    merged = {}

    for document, score in lexical_results:
        key = _normalize_message(document.page_content)
        merged[key] = {
            "document": document,
            "lexical_score": score,
            "vector_score": 0.0,
        }

    for document, score in vector_results:
        if _is_table_of_contents_chunk(document.page_content):
            continue

        key = _normalize_message(document.page_content)
        lexical_score = float(_lexical_score(question, document.page_content))

        if key not in merged:
            merged[key] = {
                "document": document,
                "lexical_score": lexical_score,
                "vector_score": score,
            }
        else:
            merged[key]["vector_score"] = max(merged[key]["vector_score"], score)
            merged[key]["lexical_score"] = max(
                merged[key]["lexical_score"], lexical_score
            )

    ranked_results = sorted(
        merged.values(),
        key=lambda item: (item["lexical_score"] * 10) + item["vector_score"],
        reverse=True,
    )

    relevant_results = []

    for item in ranked_results:
        if not _passes_relevance_gate(
            question,
            item["document"].page_content,
            item["lexical_score"],
            item["vector_score"],
        ):
            continue

        relevant_results.append(
            (item["document"], item["vector_score"] or item["lexical_score"])
        )

        if len(relevant_results) >= TOP_K:
            break

    return relevant_results


def retrieve_relevant_documents(question):
    """Retrieve ranked document chunks (Chroma first, lexical boost, relevance gate)."""
    vector_results = _retrieve_from_vector_store(question)
    lexical_results = _retrieve_from_local_chunks(question)

    if not vector_results and not lexical_results:
        return []

    return _merge_results(question, lexical_results, vector_results)


def _retrieve_relevant_documents(question):
    return retrieve_relevant_documents(question)


def ask_question(question):
    if _is_greeting(question):
        return EXACT_GREETING_RESPONSE

    relevant_documents = _retrieve_relevant_documents(question)

    if not relevant_documents:
        return EXACT_FALLBACK_RESPONSE

    context = "\n\n".join(
        document.page_content.strip()
        for document, _score in relevant_documents
    )
    retrieval_question = _refine_question(question) or question

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

RETRIEVED CONTEXT:
{context}

USER QUESTION:
{question}

RETRIEVAL QUESTION:
{retrieval_question}
"""

    llm = get_llm()
    response = llm.invoke(prompt)
    answer = response.content.strip()

    if EXACT_FALLBACK_RESPONSE.lower() in answer.lower():
        return EXACT_FALLBACK_RESPONSE

    return answer
