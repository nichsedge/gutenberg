import math
import re
from typing import Dict, Any, List
from collections import Counter
from analyzer.nltk_helper import tokenize_words, tokenize_sentences, STOPWORDS

def count_syllables(word: str) -> int:
    """Estimate syllables in an English word for readability formulas."""
    word = word.lower().strip(".:;?!'\"")
    if not word:
        return 0
    if len(word) <= 3:
        return 1
    word = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', word)
    word = re.sub(r'^y', '', word)
    syllables = len(re.findall(r'[aeiouy]{1,2}', word))
    return max(1, syllables)

def calculate_basic_statistics(book_data: Dict[str, Any]) -> Dict[str, Any]:
    """Compute comprehensive basic statistics for the ebook."""
    clean_text = book_data["clean_text"]
    words = tokenize_words(clean_text)
    sentences = tokenize_sentences(clean_text)
    chapters = book_data.get("chapters", [])
    verses = book_data.get("verses", [])

    total_words = len(words)
    if total_words == 0:
        return {"error": "Book is empty or could not be tokenized."}

    word_counts = Counter(words)
    unique_words = len(word_counts)
    total_characters = len(clean_text)
    total_chars_no_spaces = len(re.sub(r'\s+', '', clean_text))
    total_sentences = max(1, len(sentences))
    total_verses = len(verses) if verses else total_sentences

    # Lexical Diversity metrics
    ttr = round((unique_words / total_words) * 100, 2)  # Type-Token Ratio %
    hapax_legomena = sum(1 for count in word_counts.values() if count == 1)
    hapax_ratio = round((hapax_legomena / unique_words) * 100, 2)
    dis_legomena = sum(1 for count in word_counts.values() if count == 2)

    # Word Length distribution
    word_lengths = [len(w) for w in words]
    avg_word_length = round(sum(word_lengths) / total_words, 2)
    length_distribution = Counter(word_lengths)

    # Sentence metrics
    sent_lengths = [len(tokenize_words(s)) for s in sentences if s.strip()]
    avg_sentence_length = round(sum(sent_lengths) / len(sent_lengths), 2) if sent_lengths else 0
    max_sentence_length = max(sent_lengths) if sent_lengths else 0
    min_sentence_length = min(sent_lengths) if sent_lengths else 0

    # Syllables and Readability Scores
    total_syllables = sum(count_syllables(w) for w in words)
    complex_words = sum(1 for w in words if count_syllables(w) >= 3)
    pct_complex = (complex_words / total_words) * 100

    # Flesch Reading Ease: 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
    flesch_ease = round(206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words), 2)
    # Flesch-Kincaid Grade Level: 0.39*(words/sentences) + 11.8*(syllables/words) - 15.59
    fk_grade = round(0.39 * (total_words / total_sentences) + 11.8 * (total_syllables / total_words) - 15.59, 2)
    # Gunning Fog Index: 0.4 * ((words/sentences) + 100*(complex_words/words))
    gunning_fog = round(0.4 * ((total_words / total_sentences) + pct_complex), 2)

    # Stopwords vs Content words
    stopwords_count = sum(word_counts[w] for w in word_counts if w in STOPWORDS)
    content_words_count = total_words - stopwords_count
    lexical_density = round((content_words_count / total_words) * 100, 2)

    # Reading Time estimation (200 words/min average silent reading speed)
    reading_time_minutes = round(total_words / 200)

    # Chapter length progression
    chapter_stats = []
    for chap in chapters:
        c_words = tokenize_words(chap["text"])
        chapter_stats.append({
            "id": chap["id"],
            "title": chap["title"][:50],
            "word_count": len(c_words),
            "char_count": len(chap["text"])
        })

    return {
        "title": book_data.get("title", "Unknown"),
        "author": book_data.get("author", "Friedrich Nietzsche"),
        "total_words": total_words,
        "unique_words": unique_words,
        "total_characters": total_characters,
        "total_chars_no_spaces": total_chars_no_spaces,
        "total_sentences": total_sentences,
        "total_verses": total_verses,
        "total_chapters": len(chapters),
        "type_token_ratio": ttr,
        "hapax_legomena": hapax_legomena,
        "hapax_percentage": hapax_ratio,
        "dis_legomena": dis_legomena,
        "lexical_density": lexical_density,
        "average_word_length": avg_word_length,
        "average_sentence_length": avg_sentence_length,
        "max_sentence_length": max_sentence_length,
        "min_sentence_length": min_sentence_length,
        "flesch_reading_ease": flesch_ease,
        "flesch_kincaid_grade": fk_grade,
        "gunning_fog_index": gunning_fog,
        "complex_words_count": complex_words,
        "complex_words_percentage": round(pct_complex, 2),
        "estimated_reading_minutes": reading_time_minutes,
        "word_length_distribution": [
            {"length": l, "count": count}
            for l, count in sorted(length_distribution.items()) if 1 <= l <= 18
        ],
        "chapter_stats": chapter_stats
    }
