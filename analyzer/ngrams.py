from typing import Dict, Any, List, Optional
from collections import Counter
from analyzer.nltk_helper import tokenize_words, STOPWORDS

def calculate_ngrams(
    book_data: Dict[str, Any],
    n: int = 2,
    filter_stopwords: bool = False,
    min_count: int = 2,
    search_query: Optional[str] = None,
    limit: int = 200
) -> Dict[str, Any]:
    """Extract n-grams (2 to 5) with frequency and sample locations."""
    clean_text = book_data["clean_text"]
    words = tokenize_words(clean_text)

    if len(words) < n:
        return {"n": n, "total_ngrams": 0, "unique_ngrams": 0, "results": []}

    ngram_counts = Counter()
    ngram_locations = {}

    for i in range(len(words) - n + 1):
        gram_tokens = words[i:i+n]
        if filter_stopwords and all(t in STOPWORDS for t in gram_tokens):
            continue
        gram_str = " ".join(gram_tokens)
        ngram_counts[gram_str] += 1
        if gram_str not in ngram_locations:
            ngram_locations[gram_str] = []
        if len(ngram_locations[gram_str]) < 3:
            # save sample window
            start_ctx = max(0, i - 4)
            end_ctx = min(len(words), i + n + 4)
            ngram_locations[gram_str].append(" ".join(words[start_ctx:end_ctx]))

    total_ngrams_generated = sum(ngram_counts.values())

    results = []
    for gram, count in ngram_counts.most_common():
        if count < min_count:
            continue
        if search_query and search_query.lower() not in gram:
            continue

        pct = round((count / total_ngrams_generated) * 100, 4) if total_ngrams_generated else 0
        results.append({
            "ngram": gram,
            "count": count,
            "percentage": pct,
            "sample_contexts": ngram_locations.get(gram, [])
        })

        if len(results) >= limit:
            break

    return {
        "n": n,
        "total_ngrams": total_ngrams_generated,
        "unique_ngrams": len(ngram_counts),
        "results": results
    }
