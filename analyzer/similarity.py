import math
from typing import Dict, Any, List, Optional
from collections import Counter
import numpy as np
from analyzer.nltk_helper import tokenize_words, STOPWORDS

def build_cooccurrence_vectors(words: List[str], vocab: List[str], window_size: int = 4) -> Dict[str, np.ndarray]:
    """Build word vector space based on sliding window co-occurrence."""
    vocab_idx = {w: i for i, w in enumerate(vocab)}
    vocab_size = len(vocab)
    matrix = {w: np.zeros(vocab_size, dtype=np.float32) for w in vocab}

    for i, w in enumerate(words):
        if w not in vocab_idx:
            continue
        start = max(0, i - window_size)
        end = min(len(words), i + window_size + 1)
        for j in range(start, end):
            if i != j:
                context_word = words[j]
                if context_word in vocab_idx:
                    matrix[w][vocab_idx[context_word]] += 1.0

    # Apply PPMI (Positive Pointwise Mutual Information) weighting
    total_sum = sum(np.sum(vec) for vec in matrix.values())
    if total_sum > 0:
        col_sums = np.zeros(vocab_size, dtype=np.float32)
        for vec in matrix.values():
            col_sums += vec

        for w, vec in matrix.items():
            row_sum = np.sum(vec)
            if row_sum > 0:
                expected = (row_sum * col_sums) / total_sum
                with np.errstate(divide='ignore', invalid='ignore'):
                    pmi = np.log2((vec * total_sum) / (row_sum * col_sums + 1e-9))
                    pmi[pmi < 0] = 0
                    pmi[np.isnan(pmi)] = 0
                norm = np.linalg.norm(pmi)
                matrix[w] = pmi / norm if norm > 0 else pmi

    return matrix

def get_word_similarity(
    book_data: Dict[str, Any],
    word1: str,
    word2: Optional[str] = None,
    top_k: int = 15
) -> Dict[str, Any]:
    """
    Calculate semantic vector similarity for target word(s) in the ebook corpus.
    """
    w1 = word1.strip().lower()
    clean_text = book_data["clean_text"]
    words = tokenize_words(clean_text)

    # Build vocab of top content words
    counts = Counter(words)
    content_vocab = [w for w, c in counts.most_common(1200) if w not in STOPWORDS and len(w) > 2]
    if w1 not in content_vocab:
        content_vocab.append(w1)
    if word2:
        w2 = word2.strip().lower()
        if w2 not in content_vocab:
            content_vocab.append(w2)

    vectors = build_cooccurrence_vectors(words, content_vocab, window_size=4)

    if w1 not in vectors:
        return {"error": f"Word '{w1}' is too rare or not found in text."}

    v1 = vectors[w1]
    norm1 = np.linalg.norm(v1)

    # Pairwise comparison mode
    if word2:
        w2 = word2.strip().lower()
        if w2 not in vectors:
            return {"error": f"Word '{w2}' is too rare or not found in text."}
        v2 = vectors[w2]
        norm2 = np.linalg.norm(v2)
        cos_sim = float(np.dot(v1, v2) / (norm1 * norm2)) if norm1 > 0 and norm2 > 0 else 0.0
        return {
            "mode": "pairwise",
            "word1": w1,
            "word2": w2,
            "cosine_similarity": round(cos_sim, 4),
            "percentage_similarity": round(max(0.0, cos_sim) * 100, 2)
        }

    # Nearest neighbors mode
    similarities = []
    for other_word, v2 in vectors.items():
        if other_word == w1:
            continue
        norm2 = np.linalg.norm(v2)
        if norm1 > 0 and norm2 > 0:
            sim = float(np.dot(v1, v2) / (norm1 * norm2))
            similarities.append({
                "word": other_word,
                "similarity": round(sim, 4),
                "similarity_score": round(max(0.0, sim) * 100, 1),
                "frequency": counts.get(other_word, 0)
            })

    similarities.sort(key=lambda x: x["similarity"], reverse=True)

    return {
        "mode": "nearest_neighbors",
        "target_word": w1,
        "occurrences": counts.get(w1, 0),
        "similar_words": similarities[:top_k]
    }
