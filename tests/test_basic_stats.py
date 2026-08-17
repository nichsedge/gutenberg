"""Tests for analyzer/basic_stats.py"""
import pytest
from analyzer.basic_stats import count_syllables, calculate_basic_statistics


class TestCountSyllables:
    def test_single_syllable(self):
        assert count_syllables("man") == 1
        assert count_syllables("bridge") >= 1

    def test_multi_syllable(self):
        assert count_syllables("philosopher") >= 3
        assert count_syllables("eternal") >= 2

    def test_empty_string(self):
        assert count_syllables("") == 0

    def test_minimum_one(self):
        # Should return at least 1 for any valid word
        assert count_syllables("a") >= 1
        assert count_syllables("the") >= 1


class TestCalculateBasicStatistics:
    def test_returns_required_keys(self, fixture_book):
        stats = calculate_basic_statistics(fixture_book)
        required_keys = [
            "title", "author", "total_words", "unique_words", "total_characters",
            "total_sentences", "type_token_ratio", "hapax_legomena",
            "flesch_reading_ease", "flesch_kincaid_grade", "estimated_reading_minutes",
            "word_length_distribution", "chapter_stats",
        ]
        for key in required_keys:
            assert key in stats, f"Missing key: {key}"

    def test_total_words_positive(self, fixture_book):
        stats = calculate_basic_statistics(fixture_book)
        assert stats["total_words"] > 0

    def test_unique_words_leq_total(self, fixture_book):
        stats = calculate_basic_statistics(fixture_book)
        assert stats["unique_words"] <= stats["total_words"]

    def test_ttr_is_percentage(self, fixture_book):
        stats = calculate_basic_statistics(fixture_book)
        assert 0 < stats["type_token_ratio"] <= 100

    def test_hapax_ratio_is_percentage(self, fixture_book):
        stats = calculate_basic_statistics(fixture_book)
        assert 0 <= stats["hapax_percentage"] <= 100

    def test_reading_time_positive(self, fixture_book):
        stats = calculate_basic_statistics(fixture_book)
        assert stats["estimated_reading_minutes"] >= 0

    def test_chapter_stats_count(self, fixture_book):
        stats = calculate_basic_statistics(fixture_book)
        assert len(stats["chapter_stats"]) == fixture_book["total_chapters"]

    def test_empty_book(self):
        empty_book = {
            "clean_text": "",
            "chapters": [],
            "verses": [],
        }
        result = calculate_basic_statistics(empty_book)
        assert "error" in result
