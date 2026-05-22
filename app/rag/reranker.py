from functools import lru_cache

_cross_encoder = None


@lru_cache(maxsize=1)
def _get_cross_encoder():
    from sentence_transformers import CrossEncoder

    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank_pairs(question, documents):
    if not documents:
        return []

    model = _get_cross_encoder()
    pairs = [[question, document.page_content] for document in documents]
    scores = model.predict(pairs)
    return [float(score) for score in scores]
