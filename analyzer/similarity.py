"""
Word similarity via co-occurrence vector space with PPMI weighting.
Uses scipy sparse matrices for memory efficiency.
"""
import math
from typing import Dict, Any, List, Optional
from collections import Counter

import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.linalg import norm as sparse_norm

from analyzer.nltk_helper import tokenize_words, STOPWORDS

# Module-level cache: book_id → (vectors dict, counts dict)
_similarity_cache: Dict[str, tuple] = {}


def _build_ppmi_vectors(
    words: List[str], vocab: List[str], window_size: int = 4
) -> Dict[str, np.ndarray]:
    """
    Build PPMI-weighted co-occurrence vectors using scipy sparse matrices.
    Dramatically reduces memory vs. a dict of dense np.ndarray.
    """
    vocab_idx = {w: i for i, w in enumerate(vocab)}
    V = len(vocab)
    n_words = len(words)

    # Build sparse co-occurrence matrix
    cooc = lil_matrix((V, V), dtype=np.float32)
    for i, w in enumerate(words):
        if w not in vocab_idx:
            continue
        wi = vocab_idx[w]
        start = max(0, i - window_size)
        end = min(n_words, i + window_size + 1)
        for j in range(start, end):
            if i != j:
                cw = words[j]
                if cw in vocab_idx:
                    cooc[wi, vocab_idx[cw]] += 1.0

    cooc_csr = cooc.tocsr()
    total = cooc_csr.sum()
    if total == 0:
        return {w: np.zeros(V, dtype=np.float32) for w in vocab}

    row_sums = np.asarray(cooc_csr.sum(axis=1)).flatten()  # shape (V,)
    col_sums = np.asarray(cooc_csr.sum(axis=0)).flatten()  # shape (V,)

    # Compute PPMI and build dense row vectors per word
    vectors: Dict[str, np.ndarray] = {}
    for w in vocab:
        wi = vocab_idx[w]
        row = cooc_csr.getrow(wi).toarray().flatten()
        rs = row_sums[wi]
        if rs == 0:
            vectors[w] = np.zeros(V, dtype=np.float32)
            continue

        with np.errstate(divide="ignore", invalid="ignore"):
            pmi = np.log2((row * total) / (rs * col_sums + 1e-9))
        pmi = np.where((pmi > 0) & np.isfinite(pmi), pmi, 0.0).astype(np.float32)
        norm = np.linalg.norm(pmi)
        vectors[w] = (pmi / norm) if norm > 0 else pmi

    return vectors


def _get_vectors(book_data: Dict[str, Any]) -> tuple:
    """Return (vectors, counts) for a book, using cache to avoid recomputation."""
    book_id = book_data.get("id", "__unknown__")
    if book_id in _similarity_cache:
        return _similarity_cache[book_id]

    words = tokenize_words(book_data["clean_text"])
    counts = Counter(words)
    content_vocab = [w for w, c in counts.most_common(1200) if w not in STOPWORDS and len(w) > 2]

    vectors = _build_ppmi_vectors(words, content_vocab, window_size=4)
    _similarity_cache[book_id] = (vectors, counts)
    return vectors, counts


def get_word_similarity(
    book_data: Dict[str, Any],
    word1: str,
    word2: Optional[str] = None,
    top_k: int = 15,
) -> Dict[str, Any]:
    """
    Compute semantic vector similarity for target word(s) in the ebook corpus.
    Builds/caches the PPMI vector space once per book.
    """
    w1 = word1.strip().lower()
    vectors, counts = _get_vectors(book_data)

    # If word not in cache vocab, it's too rare
    if w1 not in vectors:
        return {"error": f"Word '{w1}' is too rare or not found in the text."}

    v1 = vectors[w1]
    norm1 = np.linalg.norm(v1)

    if word2:
        w2 = word2.strip().lower()
        if w2 not in vectors:
            return {"error": f"Word '{w2}' is too rare or not found in the text."}
        v2 = vectors[w2]
        norm2 = np.linalg.norm(v2)
        cos = float(np.dot(v1, v2) / (norm1 * norm2)) if norm1 > 0 and norm2 > 0 else 0.0
        return {
            "mode": "pairwise",
            "word1": w1,
            "word2": w2,
            "cosine_similarity": round(cos, 4),
            "percentage_similarity": round(max(0.0, cos) * 100, 2),
        }

    # Nearest neighbors
    sims = []
    for other, v2 in vectors.items():
        if other == w1:
            continue
        norm2 = np.linalg.norm(v2)
        if norm1 > 0 and norm2 > 0:
            s = float(np.dot(v1, v2) / (norm1 * norm2))
            sims.append({
                "word": other,
                "similarity": round(s, 4),
                "similarity_score": round(max(0.0, s) * 100, 1),
                "frequency": counts.get(other, 0),
            })

    sims.sort(key=lambda x: x["similarity"], reverse=True)

    return {
        "mode": "nearest_neighbors",
        "target_word": w1,
        "occurrences": counts.get(w1, 0),
        "similar_words": sims[:top_k],
    }
