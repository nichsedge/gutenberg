import re
from typing import Dict, Any, List, Optional
from collections import Counter
from analyzer.nltk_helper import tokenize_words, tokenize_sentences, tag_pos_tokens

def extract_pos_patterns(book_data: Dict[str, Any], pattern_length: int = 2, limit: int = 50) -> Dict[str, Any]:
    """Find the most frequent Part of Speech n-tag patterns in the ebook."""
    clean_text = book_data["clean_text"]
    words = tokenize_words(clean_text)
    tagged = tag_pos_tokens(words)

    tags_only = [pos for _, pos in tagged]
    pattern_counts = Counter()
    examples = {}

    for i in range(len(tags_only) - pattern_length + 1):
        pat = " ".join(tags_only[i:i+pattern_length])
        pattern_counts[pat] += 1
        if pat not in examples:
            sample_words = " ".join([f"{w}[{pos}]" for w, pos in tagged[i:i+pattern_length]])
            examples[pat] = sample_words

    total_patterns = sum(pattern_counts.values())
    results = []
    for pat, count in pattern_counts.most_common(limit):
        results.append({
            "pattern": pat,
            "count": count,
            "percentage": round((count / total_patterns) * 100, 2) if total_patterns else 0,
            "example": examples.get(pat, "")
        })

    return {
        "pattern_length": pattern_length,
        "total_patterns": total_patterns,
        "results": results
    }

def query_pos_pattern(
    book_data: Dict[str, Any],
    pos_query: str,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Search sentences/verses matching a specific POS pattern sequence.
    Example query: "ADJ NOUN" or "PRON VERB ADV" or "DET ADJ NOUN".
    """
    verses = book_data.get("verses", [])
    if not verses:
        sentences = tokenize_sentences(book_data["clean_text"])
        verses = [{"id": i+1, "chapter_title": "Text", "text": s} for i, s in enumerate(sentences)]

    target_tags = [t.strip().upper() for t in pos_query.strip().split() if t.strip()]
    if not target_tags:
        return {"query": pos_query, "matches_count": 0, "matches": []}

    pat_len = len(target_tags)
    matches = []

    for verse in verses:
        v_words = tokenize_words(verse["text"], lower=False)
        tagged = tag_pos_tokens(v_words)
        tags = [pos for _, pos in tagged]

        # Scan for matching sub-sequence
        for i in range(len(tags) - pat_len + 1):
            if tags[i:i+pat_len] == target_tags:
                matched_snippet = " ".join(v_words[i:i+pat_len])
                # Format tagged representation
                tagged_snippet = " ".join([f"<strong>{w}</strong><sub>{p}</sub>" for w, p in tagged[i:i+pat_len]])
                matches.append({
                    "verse_id": verse["id"],
                    "chapter_title": verse.get("chapter_title", "General"),
                    "matched_words": matched_snippet,
                    "tagged_preview": tagged_snippet,
                    "full_verse": verse["text"]
                })
                if len(matches) >= limit:
                    break
        if len(matches) >= limit:
            break

    return {
        "query": " ".join(target_tags),
        "matches_count": len(matches),
        "matches": matches
    }
