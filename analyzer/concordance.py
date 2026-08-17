"""
Key Word in Context (KWIC) concordance generator.
Supports single words, multi-word phrases, and regex patterns.
"""
import re
from typing import Dict, Any, List, Optional
from analyzer.nltk_helper import tokenize_words


def generate_concordance(
    book_data: Dict[str, Any],
    keyword: str,
    context_words: int = 7,
    chapter_filter: Optional[int] = None,
    sort_by: str = "order",  # "order", "left", "right"
    limit: int = 300,
) -> Dict[str, Any]:
    """
    Generate KWIC concordance lines for any term (single word, phrase, or regex).
    Phrases containing spaces are matched as substrings across the full verse text.
    """
    clean_keyword = keyword.strip()
    if not clean_keyword:
        return {"keyword": "", "total_matches": 0, "lines": []}

    verses = book_data.get("verses", [])
    is_phrase = " " in clean_keyword

    # Build pattern — escape plain text, allow regex if prefixed with "regex:"
    if clean_keyword.lower().startswith("regex:"):
        try:
            pattern = re.compile(clean_keyword[6:].strip(), re.IGNORECASE)
        except re.error:
            return {"keyword": clean_keyword, "error": "Invalid regex pattern", "total_matches": 0, "lines": []}
    else:
        pattern = re.compile(r"\b" + re.escape(clean_keyword) + r"\b", re.IGNORECASE)

    concordance_lines = []

    for v in verses:
        chap_id = v.get("chapter_id", 1)
        if chapter_filter is not None and chap_id != chapter_filter:
            continue

        text = v["text"]

        if is_phrase or clean_keyword.lower().startswith("regex:"):
            # Phrase / regex matching on full text
            for m in pattern.finditer(text):
                start, end = m.start(), m.end()
                left_str = text[:start].rstrip()
                right_str = text[end:].lstrip()
                # Trim context to context_words
                left_words = left_str.split()[-context_words:]
                right_words = right_str.split()[:context_words]
                concordance_lines.append({
                    "verse_id": v["id"],
                    "chapter_id": chap_id,
                    "chapter_title": v.get("chapter_title", f"Chapter {chap_id}"),
                    "left_context": " ".join(left_words),
                    "keyword": m.group(0),
                    "right_context": " ".join(right_words),
                    "full_verse": text,
                })
        else:
            # Single word — token-level matching for alignment
            words = text.split()
            kw_lower = clean_keyword.lower()
            for i, token in enumerate(words):
                clean_token = re.sub(r"[^\w]", "", token).lower()
                if clean_token == kw_lower:
                    left_tokens = words[max(0, i - context_words):i]
                    right_tokens = words[i + 1: min(len(words), i + 1 + context_words)]
                    concordance_lines.append({
                        "verse_id": v["id"],
                        "chapter_id": chap_id,
                        "chapter_title": v.get("chapter_title", f"Chapter {chap_id}"),
                        "left_context": " ".join(left_tokens),
                        "keyword": token,
                        "right_context": " ".join(right_tokens),
                        "full_verse": text,
                    })

    # Sort
    if sort_by == "left":
        concordance_lines.sort(key=lambda x: x["left_context"].lower()[::-1])
    elif sort_by == "right":
        concordance_lines.sort(key=lambda x: x["right_context"].lower())

    return {
        "keyword": clean_keyword,
        "total_matches": len(concordance_lines),
        "lines": concordance_lines[:limit],
    }
