"""
Cross-book comparative analysis module.
Compare two ebooks on vocabulary, style, readability, and concept density.
"""
from typing import Dict, Any, List
from collections import Counter

from analyzer.nltk_helper import tokenize_words, STOPWORDS
from analyzer.basic_stats import calculate_basic_statistics
from analyzer.ontology import PHILOSOPHICAL_ONTOLOGY


def compare_books(book_a: Dict[str, Any], book_b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Side-by-side comparative analysis of two ebooks.
    Returns vocabulary overlap, unique terms, readability diff, concept density, and style metrics.
    """
    stats_a = calculate_basic_statistics(book_a)
    stats_b = calculate_basic_statistics(book_b)

    words_a = tokenize_words(book_a["clean_text"])
    words_b = tokenize_words(book_b["clean_text"])

    counts_a = Counter(words_a)
    counts_b = Counter(words_b)

    vocab_a = {w for w in counts_a if w not in STOPWORDS and len(w) > 2}
    vocab_b = {w for w in counts_b if w not in STOPWORDS and len(w) > 2}

    shared = vocab_a & vocab_b
    only_a = vocab_a - vocab_b
    only_b = vocab_b - vocab_a

    jaccard_similarity = round(len(shared) / len(vocab_a | vocab_b) * 100, 2) if (vocab_a | vocab_b) else 0

    # Top unique words per book (by relative frequency difference)
    def top_unique(only: set, counts: Counter, other_counts: Counter, n=20) -> List[Dict]:
        scored = []
        total = max(1, sum(counts.values()))
        other_total = max(1, sum(other_counts.values()))
        for w in only:
            freq_here = counts[w] / total * 10000
            freq_other = other_counts.get(w, 0) / other_total * 10000
            scored.append({
                "word": w,
                "count": counts[w],
                "freq_per_10k": round(freq_here, 2),
                "exclusivity_score": round(freq_here - freq_other, 2),
            })
        scored.sort(key=lambda x: x["exclusivity_score"], reverse=True)
        return scored[:n]

    # Concept density comparison
    concept_density_a = {}
    concept_density_b = {}
    total_a = max(1, len(words_a))
    total_b = max(1, len(words_b))

    for concept, info in PHILOSOPHICAL_ONTOLOGY.items():
        kw_set = set(info["keywords"])
        count_a = sum(1 for w in words_a if w in kw_set)
        count_b = sum(1 for w in words_b if w in kw_set)
        concept_density_a[concept] = round(count_a / total_a * 10000, 2)
        concept_density_b[concept] = round(count_b / total_b * 10000, 2)

    concept_comparison = [
        {
            "concept": concept,
            "density_a": concept_density_a[concept],
            "density_b": concept_density_b[concept],
            "difference": round(concept_density_a[concept] - concept_density_b[concept], 2),
        }
        for concept in PHILOSOPHICAL_ONTOLOGY
    ]
    concept_comparison.sort(key=lambda x: abs(x["difference"]), reverse=True)

    def _stat(s: Dict, key: str):
        return s.get(key, "N/A")

    return {
        "book_a": {"id": book_a.get("id"), "title": book_a.get("title"), "author": book_a.get("author")},
        "book_b": {"id": book_b.get("id"), "title": book_b.get("title"), "author": book_b.get("author")},
        "vocabulary": {
            "jaccard_similarity_pct": jaccard_similarity,
            "shared_vocab_size": len(shared),
            "unique_to_a": len(only_a),
            "unique_to_b": len(only_b),
            "top_unique_a": top_unique(only_a, counts_a, counts_b),
            "top_unique_b": top_unique(only_b, counts_b, counts_a),
        },
        "readability": {
            "total_words_a": _stat(stats_a, "total_words"),
            "total_words_b": _stat(stats_b, "total_words"),
            "unique_words_a": _stat(stats_a, "unique_words"),
            "unique_words_b": _stat(stats_b, "unique_words"),
            "ttr_a": _stat(stats_a, "type_token_ratio"),
            "ttr_b": _stat(stats_b, "type_token_ratio"),
            "flesch_ease_a": _stat(stats_a, "flesch_reading_ease"),
            "flesch_ease_b": _stat(stats_b, "flesch_reading_ease"),
            "fk_grade_a": _stat(stats_a, "flesch_kincaid_grade"),
            "fk_grade_b": _stat(stats_b, "flesch_kincaid_grade"),
            "avg_sentence_len_a": _stat(stats_a, "average_sentence_length"),
            "avg_sentence_len_b": _stat(stats_b, "average_sentence_length"),
            "lexical_density_a": _stat(stats_a, "lexical_density"),
            "lexical_density_b": _stat(stats_b, "lexical_density"),
        },
        "concepts": concept_comparison,
    }
