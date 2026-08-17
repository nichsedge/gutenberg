import re
from typing import Dict, Any, List, Tuple
from collections import Counter
from analyzer.nltk_helper import tokenize_words, tokenize_sentences, STOPWORDS

def find_repeated_verses(
    book_data: Dict[str, Any],
    min_similarity: float = 0.8,
    min_words: int = 4,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Detect exact and near-duplicate verses/aphorisms across the ebook.
    Finds recurring philosophical motifs and repeated refrains.
    """
    verses = book_data.get("verses", [])
    if not verses:
        sentences = tokenize_sentences(book_data["clean_text"])
        verses = [{"id": i+1, "chapter_title": "General", "text": s} for i, s in enumerate(sentences)]

    # Normalized signatures for exact matching
    exact_groups: Dict[str, List[Dict[str, Any]]] = {}
    normalized_list = []

    for v in verses:
        text = v["text"].strip()
        clean = re.sub(r'[^\w\s]', '', text.lower())
        tokens = clean.split()
        if len(tokens) < min_words:
            continue
        sig = " ".join(tokens)
        if sig not in exact_groups:
            exact_groups[sig] = []
        exact_groups[sig].append(v)
        normalized_list.append((v, set(tokens), len(tokens), sig))

    # Exact repeated verses
    exact_duplicates = []
    for sig, v_list in exact_groups.items():
        if len(v_list) > 1:
            exact_duplicates.append({
                "repetition_count": len(v_list),
                "text": v_list[0]["text"],
                "occurrences": [
                    {"verse_id": x["id"], "chapter": x.get("chapter_title", "General"), "text": x["text"]}
                    for x in v_list
                ]
            })

    exact_duplicates.sort(key=lambda x: x["repetition_count"], reverse=True)

    # Near-duplicates using Jaccard token similarity
    near_duplicates = []
    seen_pairs = set()
    
    # Check sample if list is large
    sample_list = normalized_list[:1200]
    for i in range(len(sample_list)):
        v1, set1, len1, sig1 = sample_list[i]
        for j in range(i + 1, len(sample_list)):
            v2, set2, len2, sig2 = sample_list[j]
            if sig1 == sig2:
                continue
            pair_key = (min(v1["id"], v2["id"]), max(v1["id"], v2["id"]))
            if pair_key in seen_pairs:
                continue

            # Length filter
            if abs(len1 - len2) / max(len1, len2) > 0.35:
                continue

            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            if union == 0:
                continue
            jaccard = intersection / union

            if jaccard >= min_similarity:
                seen_pairs.add(pair_key)
                near_duplicates.append({
                    "similarity": round(jaccard * 100, 1),
                    "verse_a": {"id": v1["id"], "chapter": v1.get("chapter_title", ""), "text": v1["text"]},
                    "verse_b": {"id": v2["id"], "chapter": v2.get("chapter_title", ""), "text": v2["text"]}
                })
                if len(near_duplicates) >= limit:
                    break
        if len(near_duplicates) >= limit:
            break

    near_duplicates.sort(key=lambda x: x["similarity"], reverse=True)

    return {
        "exact_repeated_count": len(exact_duplicates),
        "near_duplicate_count": len(near_duplicates),
        "exact_repeats": exact_duplicates[:limit],
        "near_repeats": near_duplicates[:limit]
    }

def extract_repeated_phrases(
    book_data: Dict[str, Any],
    min_phrase_len: int = 3,
    max_phrase_len: int = 10,
    min_occurrences: int = 3,
    limit: int = 150
) -> Dict[str, Any]:
    """
    Extract recurring multi-word phrases (common substrings) across the ebook.
    Identifies aphoristic refrains, philosophical idioms, and stylistic formulas.
    """
    clean_text = book_data["clean_text"]
    words = tokenize_words(clean_text)
    total_words = len(words)

    phrase_counts = Counter()
    phrase_first_seen = {}

    # Scan window lengths
    for length in range(min_phrase_len, max_phrase_len + 1):
        for i in range(total_words - length + 1):
            chunk = words[i:i+length]
            # Ignore phrases made only of stopwords
            if all(w in STOPWORDS for w in chunk):
                continue
            phrase_str = " ".join(chunk)
            phrase_counts[phrase_str] += 1
            if phrase_str not in phrase_first_seen:
                phrase_first_seen[phrase_str] = i

    # Prune sub-phrases if a longer phrase has the exact same count
    results = []
    for phrase, count in phrase_counts.most_common():
        if count < min_occurrences:
            continue
        words_count = len(phrase.split())
        results.append({
            "phrase": phrase,
            "word_count": words_count,
            "occurrences": count,
            "relative_freq": round((count * words_count / total_words) * 10000, 2)
        })
        if len(results) >= limit:
            break

    return {
        "min_phrase_len": min_phrase_len,
        "max_phrase_len": max_phrase_len,
        "total_unique_repeated_phrases": len(results),
        "phrases": results
    }
