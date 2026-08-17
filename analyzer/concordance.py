import re
from typing import Dict, Any, List, Optional
from analyzer.nltk_helper import tokenize_words

def generate_concordance(
    book_data: Dict[str, Any],
    keyword: str,
    context_words: int = 7,
    chapter_filter: Optional[int] = None,
    sort_by: str = "order", # "order", "left", "right"
    limit: int = 300
) -> Dict[str, Any]:
    """
    Generate Key Word in Context (KWIC) concordance lines for any term.
    """
    clean_keyword = keyword.strip()
    if not clean_keyword:
        return {"keyword": "", "total_matches": 0, "lines": []}

    verses = book_data.get("verses", [])
    kw_lower = clean_keyword.lower()
    
    pattern = re.compile(r'\b(' + re.escape(clean_keyword) + r')\b', re.IGNORECASE)

    concordance_lines = []

    for v in verses:
        chap_id = v.get("chapter_id", 1)
        if chapter_filter is not None and chap_id != chapter_filter:
            continue

        text = v["text"]
        words = text.split()
        
        for i, token in enumerate(words):
            clean_token = re.sub(r'[^\w]', '', token).lower()
            if clean_token == kw_lower:
                left_tokens = words[max(0, i - context_words):i]
                matched_token = words[i]
                right_tokens = words[i + 1:min(len(words), i + 1 + context_words)]

                left_str = " ".join(left_tokens)
                right_str = " ".join(right_tokens)

                concordance_lines.append({
                    "verse_id": v["id"],
                    "chapter_id": chap_id,
                    "chapter_title": v.get("chapter_title", f"Chapter {chap_id}"),
                    "left_context": left_str,
                    "keyword": matched_token,
                    "right_context": right_str,
                    "full_verse": text
                })

    # Sort
    if sort_by == "left":
        concordance_lines.sort(key=lambda x: x["left_context"].lower()[::-1])
    elif sort_by == "right":
        concordance_lines.sort(key=lambda x: x["right_context"].lower())

    return {
        "keyword": clean_keyword,
        "total_matches": len(concordance_lines),
        "lines": concordance_lines[:limit]
    }
