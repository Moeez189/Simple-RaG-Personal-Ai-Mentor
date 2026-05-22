import re
from functools import lru_cache
from pathlib import Path

from app.utils.preprocess import clean_text

SUPPORTED_DATA_SUFFIXES = {".txt", ".md", ".pdf", ".docx"}


def _get_data_signature():
    signature = []

    for path in sorted(Path("data").rglob("*")):
        if not path.is_file():
            continue

        if path.suffix.lower() not in SUPPORTED_DATA_SUFFIXES:
            continue

        if path.as_posix().endswith("data/README.md"):
            continue

        stat = path.stat()
        signature.append((str(path), stat.st_mtime_ns, stat.st_size))

    return tuple(signature)


def _extract_terms_from_text(text):
    normalized_text = re.sub(r"[^\w\s#+.]", " ", clean_text(text).lower())
    normalized_text = re.sub(r"\s+", " ", normalized_text).strip()
    terms = set()

    for term in re.findall(r"[a-z0-9#+.]+", normalized_text):
        if len(term) > 3:
            terms.add(term)

    return terms


@lru_cache(maxsize=4)
def get_corpus_terms(_data_signature):
    terms = set()

    for path_str, _mtime, _size in _data_signature:
        path = Path(path_str)

        if path.suffix.lower() == ".pdf":
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        terms.update(_extract_terms_from_text(text))

    return tuple(sorted(terms))


def load_corpus_terms():
    return get_corpus_terms(_get_data_signature())
