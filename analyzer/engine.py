"""
EbookAnalysisEngine — central facade with:
  - Book-level cache (parsed text + metadata)
  - Analysis-level cache keyed by (book_id, analysis_type, params_hash)
  - Shared per-book token/POS/count state to avoid re-tokenizing across modules
"""
import hashlib
import json
import logging
from typing import Dict, Any, Optional

from analyzer.book_parser import BookParser
from analyzer.basic_stats import calculate_basic_statistics
from analyzer.frequency import calculate_word_frequencies
from analyzer.wordcloud_gen import get_wordcloud_data
from analyzer.ngrams import calculate_ngrams
from analyzer.pos_analyzer import extract_pos_patterns, query_pos_pattern
from analyzer.repetition import find_repeated_verses, extract_repeated_phrases
from analyzer.ontology import extract_ontology_data
from analyzer.word_info import get_word_information
from analyzer.collocation import calculate_collocations
from analyzer.concordance import generate_concordance
from analyzer.pause_marks import analyze_pause_marks
from analyzer.similarity import get_word_similarity
from analyzer.dataset_exporter import export_book_dataset
from analyzer.sentiment import analyze_sentiment
from analyzer.compare import compare_books

logger = logging.getLogger(__name__)


def _params_hash(*args, **kwargs) -> str:
    """Create a short deterministic hash from arbitrary args for cache keying."""
    raw = json.dumps({"a": args, "k": kwargs}, sort_keys=True, default=str)
    return hashlib.md5(raw.encode()).hexdigest()[:12]


class EbookAnalysisEngine:
    def __init__(self, cache_dir: str = "data/books"):
        self.parser = BookParser(cache_dir=cache_dir)
        self._book_cache: Dict[str, Dict[str, Any]] = {}
        self._analysis_cache: Dict[str, Any] = {}  # (book_id, type, hash) → result

    # ── Book loading ──────────────────────────────────────────────────────────

    def get_catalog(self):
        return self.parser.get_catalog()

    def get_book(self, book_id: str) -> Dict[str, Any]:
        if book_id not in self._book_cache:
            self._book_cache[book_id] = self.parser.fetch_or_load_book(book_id)
        return self._book_cache[book_id]

    def _cached(self, book_id: str, analysis_type: str, params_hash: str, fn, *args, **kwargs):
        """Return cached result if present, otherwise compute and store."""
        key = (book_id, analysis_type, params_hash)
        if key not in self._analysis_cache:
            self._analysis_cache[key] = fn(*args, **kwargs)
        return self._analysis_cache[key]

    # ── Analysis methods (all cached) ─────────────────────────────────────────

    def get_basic_stats(self, book_id: str):
        book = self.get_book(book_id)
        return self._cached(book_id, "stats", "v1", calculate_basic_statistics, book)

    def get_frequency(self, book_id: str, filter_stopwords=True, min_length=1,
                      pos_filter=None, search_query=None, limit=500):
        book = self.get_book(book_id)
        ph = _params_hash(filter_stopwords, min_length, pos_filter, search_query, limit)
        return self._cached(book_id, "frequency", ph,
                            calculate_word_frequencies, book, filter_stopwords,
                            min_length, pos_filter, search_query, limit)

    def get_wordcloud(self, book_id: str, max_words=150):
        book = self.get_book(book_id)
        ph = _params_hash(max_words)
        return self._cached(book_id, "wordcloud", ph, get_wordcloud_data, book, max_words)

    def get_ngrams(self, book_id: str, n=2, filter_stopwords=False, min_count=2,
                   search_query=None, limit=200):
        book = self.get_book(book_id)
        ph = _params_hash(n, filter_stopwords, min_count, search_query, limit)
        return self._cached(book_id, "ngrams", ph,
                            calculate_ngrams, book, n, filter_stopwords, min_count, search_query, limit)

    def get_pos_patterns(self, book_id: str, pattern_length=2, limit=50):
        book = self.get_book(book_id)
        ph = _params_hash(pattern_length, limit)
        return self._cached(book_id, "pos_patterns", ph,
                            extract_pos_patterns, book, pattern_length, limit)

    def query_pos(self, book_id: str, pos_query: str, limit=100):
        book = self.get_book(book_id)
        # POS queries are not cached (highly parameterised, usually unique)
        return query_pos_pattern(book, pos_query, limit)

    def get_repeated_verses(self, book_id: str, min_similarity=0.8, min_words=4, limit=100):
        book = self.get_book(book_id)
        ph = _params_hash(min_similarity, min_words, limit)
        return self._cached(book_id, "repeated_verses", ph,
                            find_repeated_verses, book, min_similarity, min_words, limit)

    def get_repeated_phrases(self, book_id: str, min_phrase_len=3, max_phrase_len=10,
                             min_occurrences=3, limit=150):
        book = self.get_book(book_id)
        ph = _params_hash(min_phrase_len, max_phrase_len, min_occurrences, limit)
        return self._cached(book_id, "repeated_phrases", ph,
                            extract_repeated_phrases, book, min_phrase_len, max_phrase_len,
                            min_occurrences, limit)

    def get_ontology(self, book_id: str):
        book = self.get_book(book_id)
        return self._cached(book_id, "ontology", "v1", extract_ontology_data, book)

    def get_word_info(self, book_id: str, word: str):
        book = self.get_book(book_id)
        return get_word_information(book, word)  # word-specific, not cached

    def get_collocations(self, book_id: str, window_size=4, min_cooccurrences=3,
                         filter_stopwords=True, target_word=None, limit=200):
        book = self.get_book(book_id)
        ph = _params_hash(window_size, min_cooccurrences, filter_stopwords, target_word, limit)
        return self._cached(book_id, "collocations", ph,
                            calculate_collocations, book, window_size, min_cooccurrences,
                            filter_stopwords, target_word, limit)

    def get_concordance(self, book_id: str, keyword: str, context_words=7,
                        chapter_filter=None, sort_by="order", limit=300):
        book = self.get_book(book_id)
        return generate_concordance(book, keyword, context_words, chapter_filter, sort_by, limit)

    def get_pause_marks(self, book_id: str):
        book = self.get_book(book_id)
        return self._cached(book_id, "pause_marks", "v1", analyze_pause_marks, book)

    def get_similarity(self, book_id: str, word1: str, word2=None, top_k=15):
        book = self.get_book(book_id)
        return get_word_similarity(book, word1, word2, top_k)

    def export_dataset(self, book_id: str, format_type="json"):
        book = self.get_book(book_id)
        return export_book_dataset(book, format_type)

    def get_sentiment(self, book_id: str):
        book = self.get_book(book_id)
        return self._cached(book_id, "sentiment", "v1", analyze_sentiment, book)

    def get_comparison(self, book_id_a: str, book_id_b: str):
        book_a = self.get_book(book_id_a)
        book_b = self.get_book(book_id_b)
        ph = _params_hash(book_id_a, book_id_b)
        return self._cached(book_id_a, f"compare_{book_id_b}", ph,
                            compare_books, book_a, book_b)

    def full_text_search(self, book_id: str, phrase: str, limit=200):
        """Multi-word full-text search returning highlighted verse matches."""
        import re
        book = self.get_book(book_id)
        phrase_clean = phrase.strip()
        if not phrase_clean:
            return {"phrase": phrase, "total_matches": 0, "results": []}

        pattern = re.compile(re.escape(phrase_clean), re.IGNORECASE)
        results = []
        for v in book.get("verses", []):
            if pattern.search(v["text"]):
                highlighted = pattern.sub(
                    lambda m: f'<mark class="highlight">{m.group(0)}</mark>', v["text"]
                )
                results.append({
                    "verse_id": v["id"],
                    "chapter_id": v.get("chapter_id", 1),
                    "chapter_title": v.get("chapter_title", ""),
                    "text": v["text"],
                    "highlighted_html": highlighted,
                })
                if len(results) >= limit:
                    break

        return {"phrase": phrase_clean, "total_matches": len(results), "results": results}
