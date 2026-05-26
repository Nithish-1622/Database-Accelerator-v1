from __future__ import annotations

import re
from collections import Counter
from typing import Dict, Iterable, List, Tuple

try:
    import spacy  # type: ignore
    _SPACY_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    spacy = None
    _SPACY_AVAILABLE = False

try:
    import nltk  # type: ignore
    from nltk.corpus import stopwords as _nltk_stopwords  # type: ignore
    _NLTK_AVAILABLE = True
except Exception:
    nltk = None
    _NLTK_AVAILABLE = False

# Minimal fallback stopword set when NLTK is not available
_FALLBACK_STOPWORDS = {
    'the', 'is', 'are', 'was', 'an', 'a', 'and', 'or', 'in', 'on', 'for', 'to', 'of', 'it', 'with', 'that', 'this'
}


def _get_stopwords() -> set:
    if _NLTK_AVAILABLE:
        try:
            return set(_nltk_stopwords.words('english'))
        except Exception:
            return _FALLBACK_STOPWORDS
    return _FALLBACK_STOPWORDS


_WORD_RE = re.compile(r"\b[\w']{2,}\b")


def simple_tokenize(text: str) -> List[str]:
    text = text.lower()
    return _WORD_RE.findall(text)


def lemmatize_tokens(tokens: List[str]) -> List[str]:
    if _SPACY_AVAILABLE:
        try:
            nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
            doc = nlp(' '.join(tokens))
            return [token.lemma_.lower() for token in doc if token.lemma_]
        except Exception:
            return tokens
    return tokens


def extract_keywords_from_text(text: str, top_k: int = 100) -> Tuple[Dict[str, int], List[Tuple[str, int]]]:
    """
    Extract keywords and frequencies from input text. Uses NLTK/Spacy when available,
    otherwise falls back to a simple regex tokenizer and a small stopword list.

    Returns (counts_dict, sorted_list)
    """
    if not text:
        return {}, []

    tokens = simple_tokenize(text)
    tokens = lemmatize_tokens(tokens)
    stopwords = _get_stopwords()
    filtered = [t for t in tokens if t not in stopwords]
    counts = Counter(filtered)
    most = counts.most_common(top_k)
    return dict(counts), most
