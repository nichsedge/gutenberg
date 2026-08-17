import math
from typing import Dict, Any, List, Optional
from collections import Counter
from analyzer.nltk_helper import tokenize_words, tag_pos_tokens, lemmatize, STOPWORDS

def calculate_word_frequencies(
    book_data: Dict[str, Any],
    filter_stopwords: bool = True,
    min_length: int = 1,
    pos_filter: Optional[str] = None,
    search_query: Optional[str] = None,
    limit: int = 500
) -> Dict[str, Any]:
    """Compute word frequency, TF-IDF, POS tags, and rank statistics."""
    clean_text = book_data["clean_text"]
    chapters = book_data.get("chapters", [])
    
    # Global tokens
    words = tokenize_words(clean_text)
    total_tokens = len(words)
    if total_tokens == 0:
        return {
            "total_corpus_words": 0,
            "unique_filtered_words": 0,
            "total_chapters": max(1, len(chapters)),
            "pos_distribution": [],
            "frequencies": [],
        }

    # POS tagging sample or full
    tagged_tokens = tag_pos_tokens(words)
    pos_map = {}
    for w, pos in tagged_tokens:
        lower_w = w.lower()
        if lower_w not in pos_map:
            pos_map[lower_w] = Counter()
        pos_map[lower_w][pos] += 1

    # Document frequency calculation (chapters as documents)
    num_docs = max(1, len(chapters))
    doc_freqs = Counter()
    for chap in chapters:
        chap_unique = set(tokenize_words(chap["text"]))
        for w in chap_unique:
            doc_freqs[w] += 1

    # Global word counts
    raw_counts = Counter(words)
    filtered_items = []

    for word, count in raw_counts.items():
        if len(word) < min_length:
            continue
        if filter_stopwords and word in STOPWORDS:
            continue
        primary_pos = pos_map[word].most_common(1)[0][0] if word in pos_map else "NOUN"
        if pos_filter and pos_filter != "ALL" and primary_pos != pos_filter:
            continue
        if search_query and search_query.lower() not in word:
            continue

        df = doc_freqs.get(word, 1)
        idf = round(math.log((num_docs + 1) / (df + 1)) + 1, 4)
        tf = count / total_tokens
        tfidf = round(tf * idf * 1000, 4)
        relative_freq = round((count / total_tokens) * 10000, 2) # per 10k words

        filtered_items.append({
            "word": word,
            "lemma": lemmatize(word, primary_pos),
            "count": count,
            "tf": round(tf, 6),
            "tf_percentage": round(tf * 100, 4),
            "relative_frequency": relative_freq,
            "document_frequency": df,
            "inverse_document_frequency": idf,
            "tfidf": tfidf,
            "pos": primary_pos
        })

    # Sort descending by count
    filtered_items.sort(key=lambda x: x["count"], reverse=True)

    # Assign ranks and cumulative percentages
    running_total = 0
    ranked_results = []
    for rank, item in enumerate(filtered_items[:limit], 1):
        running_total += item["count"]
        item["rank"] = rank
        item["cumulative_pct"] = round((running_total / total_tokens) * 100, 2)
        ranked_results.append(item)

    # Calculate Top 20 POS distribution
    pos_distribution = Counter([item["pos"] for item in filtered_items])

    return {
        "total_corpus_words": total_tokens,
        "unique_filtered_words": len(filtered_items),
        "total_chapters": num_docs,
        "pos_distribution": [{"pos": k, "count": v} for k, v in pos_distribution.most_common()],
        "frequencies": ranked_results
    }
