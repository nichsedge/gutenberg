import re
from typing import Dict, Any, List
from collections import Counter
from analyzer.nltk_helper import tokenize_words

def analyze_pause_marks(book_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze punctuation, rhetorical pauses, aphoristic cadence, and syntactic rhythm.
    Critically informative for Nietzsche's dynamic and dramatic prose style.
    """
    clean_text = book_data["clean_text"]
    words = tokenize_words(clean_text)
    total_words = max(1, len(words))
    chapters = book_data.get("chapters", [])

    # Pattern definitions for pause marks
    punctuation_patterns = {
        "Em-Dashes (—)": r'(?:—|--|–)',
        "Exclamation Marks (!)": r'!',
        "Question Marks (?)": r'\?',
        "Semicolons (;)": r';',
        "Colons (:)": r':',
        "Ellipses (...)": r'(?:\.\.\.|…)',
        "Commas (,)": r',',
        "Parentheses / Asides ()": r'\(.*?\)'
    }

    punctuation_counts = {}
    punctuation_density = {}

    for label, pat in punctuation_patterns.items():
        count = len(re.findall(pat, clean_text))
        punctuation_counts[label] = count
        punctuation_density[label] = round((count / total_words) * 1000, 2) # per 1000 words

    total_pauses = sum(punctuation_counts.values())

    # Rhetorical Cadence Metrics
    em_dash_count = punctuation_counts.get("Em-Dashes (—)", 0)
    exclamation_count = punctuation_counts.get("Exclamation Marks (!)", 0)
    question_count = punctuation_counts.get("Question Marks (?)", 0)
    semicolon_count = punctuation_counts.get("Semicolons (;)", 0)

    # Impassioned / Polemic Index: ratio of exclamation + dashes to standard periods
    impassioned_index = round(((exclamation_count + em_dash_count) / total_words) * 1000, 2)
    # Dialectical / Interrogative Index
    interrogative_index = round((question_count / total_words) * 1000, 2)
    # Complex Clause Linking Index
    aphoristic_linking_index = round((semicolon_count / total_words) * 1000, 2)

    # Chapter breakdown
    chapter_rhythm = []
    for chap in chapters:
        c_text = chap["text"]
        c_words = max(1, len(tokenize_words(c_text)))
        c_dashes = len(re.findall(r'(?:—|--|–)', c_text))
        c_excl = len(re.findall(r'!', c_text))
        c_q = len(re.findall(r'\?', c_text))
        c_semi = len(re.findall(r';', c_text))

        chapter_rhythm.append({
            "chapter_id": chap["id"],
            "title": chap["title"][:40],
            "word_count": c_words,
            "dashes_density": round((c_dashes / c_words) * 1000, 2),
            "exclamations_density": round((c_excl / c_words) * 1000, 2),
            "questions_density": round((c_q / c_words) * 1000, 2),
            "semicolons_density": round((c_semi / c_words) * 1000, 2)
        })

    return {
        "total_words": total_words,
        "total_punctuation_marks": total_pauses,
        "marks_breakdown": [
            {
                "mark": mark,
                "count": count,
                "density_per_1000_words": punctuation_density[mark]
            }
            for mark, count in punctuation_counts.items()
        ],
        "rhetorical_indices": {
            "impassioned_proclamation_index": impassioned_index,
            "dialectical_interrogation_index": interrogative_index,
            "aphoristic_clause_linking_index": aphoristic_linking_index
        },
        "chapter_rhythm": chapter_rhythm
    }
