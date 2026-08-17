import math
import re
from typing import Dict, Any, List
from collections import Counter
from analyzer.nltk_helper import tokenize_words, tag_pos_tokens, simple_lemmatize, STOPWORDS
from analyzer.basic_stats import count_syllables

def get_word_information(book_data: Dict[str, Any], query_word: str) -> Dict[str, Any]:
    """Retrieve in-depth linguistic and contextual profile for a single word."""
    word = query_word.strip().lower()
    clean_text = book_data["clean_text"]
    chapters = book_data.get("chapters", [])
    verses = book_data.get("verses", [])

    all_words = tokenize_words(clean_text)
    total_tokens = len(all_words)
    if total_tokens == 0:
        return {"error": "Corpus is empty"}

    # Word count and rank
    all_counts = Counter(all_words)
    word_count = all_counts.get(word, 0)
    
    if word_count == 0:
        return {
            "word": word,
            "found": False,
            "message": f"The word '{word}' was not found in this ebook."
        }

    # Calculate overall rank
    sorted_words = [w for w, _ in all_counts.most_common()]
    rank = sorted_words.index(word) + 1 if word in sorted_words else -1

    # Part of speech tagging instances
    pos_counts = Counter()
    collocates = Counter()
    
    # Scan windows for collocates and POS
    for i, w in enumerate(all_words):
        if w == word:
            # Collocate window ±4
            start_w = max(0, i - 4)
            end_w = min(len(all_words), i + 5)
            for j in range(start_w, end_w):
                if j != i:
                    c_word = all_words[j]
                    if c_word not in STOPWORDS and len(c_word) > 2:
                        collocates[c_word] += 1

    # POS tagging for instances
    tagged = tag_pos_tokens(all_words[:50000]) # sample if very large
    for tw, pos in tagged:
        if tw.lower() == word:
            pos_counts[pos] += 1

    # Chapter dispersion (frequency per chapter)
    chapter_dispersion = []
    for chap in chapters:
        c_words = tokenize_words(chap["text"])
        c_count = sum(1 for w in c_words if w == word)
        c_density = round((c_count / max(1, len(c_words))) * 10000, 2)
        chapter_dispersion.append({
            "chapter_id": chap["id"],
            "title": chap["title"][:40],
            "count": c_count,
            "density_per_10k": c_density
        })

    # Sample context verses
    sample_verses = []
    pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
    for v in verses:
        if pattern.search(v["text"]):
            highlighted = pattern.sub(r'<mark class="bg-amber-400/30 text-amber-200 px-1 rounded font-semibold">\g<0></mark>', v["text"])
            sample_verses.append({
                "verse_id": v["id"],
                "chapter": v.get("chapter_title", "General"),
                "text": v["text"],
                "highlighted_html": highlighted
            })
            if len(sample_verses) >= 10:
                break

    tf_pct = round((word_count / total_tokens) * 100, 4)
    relative_freq_10k = round((word_count / total_tokens) * 10000, 2)

    return {
        "word": word,
        "found": True,
        "lemma": simple_lemmatize(word),
        "syllables": count_syllables(word),
        "total_occurrences": word_count,
        "rank": rank,
        "tf_percentage": tf_pct,
        "relative_frequency_per_10k": relative_freq_10k,
        "is_stopword": word in STOPWORDS,
        "pos_breakdown": [{"pos": k, "count": v} for k, v in pos_counts.most_common()],
        "top_collocates": [{"word": k, "co_occurrences": v} for k, v in collocates.most_common(12)],
        "chapter_dispersion": chapter_dispersion,
        "sample_verses": sample_verses
    }
