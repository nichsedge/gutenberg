"""Tests for analyzer/frequency.py"""
import pytest
from analyzer.frequency import calculate_word_frequencies


class TestCalculateWordFrequencies:
    def test_returns_required_keys(self, fixture_book):
        result = calculate_word_frequencies(fixture_book)
        assert "total_corpus_words" in result
        assert "frequencies" in result
        assert "pos_distribution" in result

    def test_frequencies_sorted_by_count(self, fixture_book):
        result = calculate_word_frequencies(fixture_book)
        freqs = result["frequencies"]
        counts = [f["count"] for f in freqs]
        assert counts == sorted(counts, reverse=True), "Frequencies must be sorted descending"

    def test_stopwords_filtered(self, fixture_book):
        from analyzer.nltk_helper import STOPWORDS
        result = calculate_word_frequencies(fixture_book, filter_stopwords=True)
        words_returned = {f["word"] for f in result["frequencies"]}
        # Common stopwords should not appear when filter is on
        for sw in ["the", "is", "a", "and", "of"]:
            assert sw not in words_returned, f"Stopword '{sw}' should be filtered out"

    def test_stopwords_not_filtered(self, fixture_book):
        result = calculate_word_frequencies(fixture_book, filter_stopwords=False)
        words_returned = {f["word"] for f in result["frequencies"]}
        # At least some common stopwords should appear
        common = {"the", "is", "a", "and"}
        assert common & words_returned, "Stopwords should appear when filter is off"

    def test_rank_sequential(self, fixture_book):
        result = calculate_word_frequencies(fixture_book)
        for i, f in enumerate(result["frequencies"]):
            assert f["rank"] == i + 1

    def test_frequency_data_types(self, fixture_book):
        result = calculate_word_frequencies(fixture_book)
        for f in result["frequencies"][:5]:
            assert isinstance(f["word"], str)
            assert isinstance(f["count"], int)
            assert isinstance(f["tfidf"], float)
            assert f["count"] > 0

    def test_pos_filter(self, fixture_book):
        # When filtering to NOUN, no VERB should appear (approximately)
        result = calculate_word_frequencies(fixture_book, filter_stopwords=True, pos_filter="NOUN")
        for f in result["frequencies"]:
            assert f["pos"] == "NOUN", f"Expected NOUN but got {f['pos']} for word '{f['word']}'"

    def test_search_query(self, fixture_book):
        result = calculate_word_frequencies(fixture_book, search_query="man")
        for f in result["frequencies"]:
            assert "man" in f["word"], f"'{f['word']}' does not contain 'man'"

    def test_empty_text(self):
        empty_book = {"clean_text": "", "chapters": [], "verses": []}
        result = calculate_word_frequencies(empty_book)
        assert result["total_corpus_words"] == 0
        assert result["frequencies"] == []

    def test_tfidf_positive(self, fixture_book):
        result = calculate_word_frequencies(fixture_book)
        for f in result["frequencies"][:10]:
            assert f["tfidf"] >= 0, f"TF-IDF should be non-negative for '{f['word']}'"
