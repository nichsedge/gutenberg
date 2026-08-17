import math
from typing import Dict, Any, List, Optional
from collections import Counter
from analyzer.nltk_helper import tokenize_words, STOPWORDS

def calculate_collocations(
    book_data: Dict[str, Any],
    window_size: int = 4,
    min_cooccurrences: int = 3,
    filter_stopwords: bool = True,
    target_word: Optional[str] = None,
    limit: int = 200
) -> Dict[str, Any]:
    """
    Calculate word collocations with Pointwise Mutual Information (PMI),
    Normalized PMI (NPMI), and T-Score.
    """
    clean_text = book_data["clean_text"]
    words = tokenize_words(clean_text)
    total_tokens = len(words)

    if total_tokens < 10:
        return {"collocations": [], "total": 0}

    unigram_counts = Counter(words)
    bigram_counts = Counter()

    target = target_word.strip().lower() if target_word else None

    # Slide window
    for i in range(total_tokens):
        w1 = words[i]
        if filter_stopwords and w1 in STOPWORDS:
            continue
        if len(w1) < 2:
            continue
        if target and w1 != target:
            continue

        end_window = min(total_tokens, i + window_size + 1)
        for j in range(i + 1, end_window):
            w2 = words[j]
            if filter_stopwords and w2 in STOPWORDS:
                continue
            if len(w2) < 2:
                continue
            if w1 == w2:
                continue

            pair = (min(w1, w2), max(w1, w2))
            bigram_counts[pair] += 1

    results = []
    total_windows = max(1, total_tokens * window_size)

    for (w1, w2), co_count in bigram_counts.items():
        if co_count < min_cooccurrences:
            continue

        c1 = unigram_counts[w1]
        c2 = unigram_counts[w2]

        p_w1 = c1 / total_tokens
        p_w2 = c2 / total_tokens
        p_joint = co_count / total_windows

        expected = (c1 * c2 * window_size) / total_tokens

        # PMI = log2( P(w1, w2) / (P(w1)*P(w2)) )
        ratio = p_joint / (p_w1 * p_w2)
        pmi = round(math.log2(ratio), 3) if ratio > 0 else 0

        # NPMI = PMI / -log2(P(w1, w2))
        npmi = round(pmi / (-math.log2(p_joint)), 3) if p_joint > 0 and p_joint < 1 else 0

        # T-score = (co_count - expected) / sqrt(co_count)
        t_score = round((co_count - expected) / math.sqrt(co_count), 2) if co_count > 0 else 0

        results.append({
            "word1": w1,
            "word2": w2,
            "pair": f"{w1} — {w2}",
            "cooccurrences": co_count,
            "freq_w1": c1,
            "freq_w2": c2,
            "pmi": pmi,
            "npmi": npmi,
            "t_score": t_score
        })

    # Sort primarily by PMI or co-occurrences
    results.sort(key=lambda x: (x["pmi"], x["cooccurrences"]), reverse=True)

    return {
        "window_size": window_size,
        "total_collocations_found": len(results),
        "results": results[:limit]
    }
