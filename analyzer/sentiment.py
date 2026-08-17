"""
Sentiment analysis module using NLTK VADER.
Produces per-chapter sentiment arcs and aggregate corpus-level scores.
"""
from typing import Dict, Any, List
from analyzer.nltk_helper import NLTK_AVAILABLE

# VADER lexicon constants
_POSITIVE_THRESHOLD = 0.05
_NEGATIVE_THRESHOLD = -0.05


def _vader_scores(text: str) -> Dict[str, float]:
    """Return VADER sentiment scores for a text string."""
    if NLTK_AVAILABLE:
        try:
            from nltk.sentiment.vader import SentimentIntensityAnalyzer
            _sia = SentimentIntensityAnalyzer()
            return _sia.polarity_scores(text)
        except Exception:
            pass
    # Fallback: simple lexicon-based estimate
    return _simple_polarity(text)


def _simple_polarity(text: str) -> Dict[str, float]:
    """Very basic polarity estimator as fallback when VADER is unavailable."""
    positive_words = {
        "joy", "great", "wonderful", "beautiful", "noble", "strong", "power", "glory",
        "love", "light", "wisdom", "life", "free", "will", "create", "overcome", "yes",
    }
    negative_words = {
        "pain", "death", "suffering", "evil", "hate", "fear", "darkness", "slave",
        "pity", "weak", "despair", "nihilism", "void", "guilt", "shame", "sorrow",
    }
    words = text.lower().split()
    n = max(1, len(words))
    pos = sum(1 for w in words if w in positive_words) / n
    neg = sum(1 for w in words if w in negative_words) / n
    neu = max(0.0, 1.0 - pos - neg)
    compound = round(pos - neg, 4)
    return {"pos": round(pos, 4), "neg": round(neg, 4), "neu": round(neu, 4), "compound": compound}


def _classify_sentiment(compound: float) -> str:
    if compound >= _POSITIVE_THRESHOLD:
        return "positive"
    if compound <= _NEGATIVE_THRESHOLD:
        return "negative"
    return "neutral"


def analyze_sentiment(book_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run VADER sentiment analysis per chapter and across the full corpus.
    Returns chapter-level arcs and aggregate statistics.
    """
    chapters = book_data.get("chapters", [])
    verses = book_data.get("verses", [])

    # Chapter-level sentiment arc
    chapter_sentiments: List[Dict[str, Any]] = []
    all_compounds: List[float] = []

    for chap in chapters:
        text = chap.get("text", "")
        if not text.strip():
            continue

        scores = _vader_scores(text)
        compound = scores.get("compound", 0.0)
        all_compounds.append(compound)

        chapter_sentiments.append({
            "chapter_id": chap["id"],
            "title": chap["title"][:60],
            "word_count": len(text.split()),
            "compound": round(compound, 4),
            "positive": round(scores.get("pos", 0.0), 4),
            "negative": round(scores.get("neg", 0.0), 4),
            "neutral": round(scores.get("neu", 0.0), 4),
            "sentiment": _classify_sentiment(compound),
        })

    # Corpus-level aggregate
    total_chapters = len(chapter_sentiments)
    if total_chapters == 0:
        return {"error": "No chapters found for sentiment analysis."}

    avg_compound = round(sum(all_compounds) / total_chapters, 4)
    positive_count = sum(1 for c in chapter_sentiments if c["sentiment"] == "positive")
    negative_count = sum(1 for c in chapter_sentiments if c["sentiment"] == "negative")
    neutral_count = total_chapters - positive_count - negative_count

    most_positive = max(chapter_sentiments, key=lambda x: x["compound"])
    most_negative = min(chapter_sentiments, key=lambda x: x["compound"])

    # Verse-level sample extremes (top 5 most positive, top 5 most negative)
    verse_scores = []
    sample_size = min(len(verses), 800)  # Limit for performance
    for v in verses[:sample_size]:
        sc = _vader_scores(v["text"])
        verse_scores.append((sc["compound"], v))

    verse_scores.sort(key=lambda x: x[0], reverse=True)
    top_positive_verses = [
        {
            "verse_id": v["id"],
            "chapter": v.get("chapter_title", ""),
            "text": v["text"],
            "compound": round(s, 4),
        }
        for s, v in verse_scores[:5]
    ]
    top_negative_verses = [
        {
            "verse_id": v["id"],
            "chapter": v.get("chapter_title", ""),
            "text": v["text"],
            "compound": round(s, 4),
        }
        for s, v in verse_scores[-5:][::-1]
    ]

    return {
        "book_title": book_data.get("title", ""),
        "total_chapters_analyzed": total_chapters,
        "overall_sentiment": _classify_sentiment(avg_compound),
        "average_compound": avg_compound,
        "positive_chapters": positive_count,
        "negative_chapters": negative_count,
        "neutral_chapters": neutral_count,
        "most_positive_chapter": most_positive,
        "most_negative_chapter": most_negative,
        "chapter_arcs": chapter_sentiments,
        "top_positive_verses": top_positive_verses,
        "top_negative_verses": top_negative_verses,
    }
