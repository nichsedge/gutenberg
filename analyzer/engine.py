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

class EbookAnalysisEngine:
    def __init__(self, cache_dir: str = "data/books"):
        self.parser = BookParser(cache_dir=cache_dir)
        self._book_cache: Dict[str, Dict[str, Any]] = {}
        self._analysis_cache: Dict[str, Dict[str, Any]] = {}

    def get_catalog(self):
        return self.parser.get_catalog()

    def get_book(self, book_id: str) -> Dict[str, Any]:
        if book_id not in self._book_cache:
            self._book_cache[book_id] = self.parser.fetch_or_load_book(book_id)
        return self._book_cache[book_id]

    def get_basic_stats(self, book_id: str):
        book = self.get_book(book_id)
        return calculate_basic_statistics(book)

    def get_frequency(self, book_id: str, filter_stopwords=True, min_length=1, pos_filter=None, search_query=None, limit=500):
        book = self.get_book(book_id)
        return calculate_word_frequencies(book, filter_stopwords, min_length, pos_filter, search_query, limit)

    def get_wordcloud(self, book_id: str, max_words=150):
        book = self.get_book(book_id)
        return get_wordcloud_data(book, max_words)

    def get_ngrams(self, book_id: str, n=2, filter_stopwords=False, min_count=2, search_query=None, limit=200):
        book = self.get_book(book_id)
        return calculate_ngrams(book, n, filter_stopwords, min_count, search_query, limit)

    def get_pos_patterns(self, book_id: str, pattern_length=2, limit=50):
        book = self.get_book(book_id)
        return extract_pos_patterns(book, pattern_length, limit)

    def query_pos(self, book_id: str, pos_query: str, limit=100):
        book = self.get_book(book_id)
        return query_pos_pattern(book, pos_query, limit)

    def get_repeated_verses(self, book_id: str, min_similarity=0.8, min_words=4, limit=100):
        book = self.get_book(book_id)
        return find_repeated_verses(book, min_similarity, min_words, limit)

    def get_repeated_phrases(self, book_id: str, min_phrase_len=3, max_phrase_len=10, min_occurrences=3, limit=150):
        book = self.get_book(book_id)
        return extract_repeated_phrases(book, min_phrase_len, max_phrase_len, min_occurrences, limit)

    def get_ontology(self, book_id: str):
        book = self.get_book(book_id)
        return extract_ontology_data(book)

    def get_word_info(self, book_id: str, word: str):
        book = self.get_book(book_id)
        return get_word_information(book, word)

    def get_collocations(self, book_id: str, window_size=4, min_cooccurrences=3, filter_stopwords=True, target_word=None, limit=200):
        book = self.get_book(book_id)
        return calculate_collocations(book, window_size, min_cooccurrences, filter_stopwords, target_word, limit)

    def get_concordance(self, book_id: str, keyword: str, context_words=7, chapter_filter=None, sort_by="order", limit=300):
        book = self.get_book(book_id)
        return generate_concordance(book, keyword, context_words, chapter_filter, sort_by, limit)

    def get_pause_marks(self, book_id: str):
        book = self.get_book(book_id)
        return analyze_pause_marks(book)

    def get_similarity(self, book_id: str, word1: str, word2=None, top_k=15):
        book = self.get_book(book_id)
        return get_word_similarity(book, word1, word2, top_k)

    def export_dataset(self, book_id: str, format_type="json"):
        book = self.get_book(book_id)
        return export_book_dataset(book, format_type)
