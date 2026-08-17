"""Tests for analyzer/sentiment.py"""
import pytest
from analyzer.sentiment import analyze_sentiment, _classify_sentiment, _vader_scores


class TestClassifySentiment:
    def test_positive(self):
        assert _classify_sentiment(0.5) == "positive"
        assert _classify_sentiment(0.05) == "positive"

    def test_negative(self):
        assert _classify_sentiment(-0.5) == "negative"
        assert _classify_sentiment(-0.05) == "negative"

    def test_neutral(self):
        assert _classify_sentiment(0.0) == "neutral"
        assert _classify_sentiment(0.04) == "neutral"
        assert _classify_sentiment(-0.04) == "neutral"


class TestVaderScores:
    def test_returns_required_keys(self):
        scores = _vader_scores("This is wonderful and great!")
        assert "compound" in scores
        assert "pos" in scores
        assert "neg" in scores
        assert "neu" in scores

    def test_scores_sum_approx_one(self):
        scores = _vader_scores("The noble warrior seeks power and freedom.")
        total = scores["pos"] + scores["neg"] + scores["neu"]
        assert abs(total - 1.0) < 0.1, f"pos+neg+neu should ≈ 1.0, got {total}"

    def test_positive_text(self):
        scores = _vader_scores("This is a wonderful, joyful, and beautiful day!")
        assert scores["pos"] >= scores["neg"], "Positive text should have higher pos than neg"

    def test_negative_text(self):
        scores = _vader_scores("Death, suffering, pain, darkness, and despair.")
        # Just check compound is not strongly positive
        assert scores["compound"] <= 0.5


class TestAnalyzeSentiment:
    def test_returns_required_keys(self, fixture_book):
        result = analyze_sentiment(fixture_book)
        required_keys = [
            "book_title", "total_chapters_analyzed", "overall_sentiment",
            "average_compound", "positive_chapters", "negative_chapters",
            "neutral_chapters", "chapter_arcs", "most_positive_chapter",
            "most_negative_chapter",
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_chapter_arcs_count(self, fixture_book):
        result = analyze_sentiment(fixture_book)
        assert len(result["chapter_arcs"]) == fixture_book["total_chapters"]

    def test_chapter_counts_sum(self, fixture_book):
        result = analyze_sentiment(fixture_book)
        total = result["positive_chapters"] + result["negative_chapters"] + result["neutral_chapters"]
        assert total == result["total_chapters_analyzed"]

    def test_chapter_arc_keys(self, fixture_book):
        result = analyze_sentiment(fixture_book)
        for arc in result["chapter_arcs"]:
            assert "chapter_id" in arc
            assert "compound" in arc
            assert "sentiment" in arc
            assert arc["sentiment"] in {"positive", "negative", "neutral"}

    def test_compound_in_range(self, fixture_book):
        result = analyze_sentiment(fixture_book)
        assert -1.0 <= result["average_compound"] <= 1.0
        for arc in result["chapter_arcs"]:
            assert -1.0 <= arc["compound"] <= 1.0

    def test_empty_chapters(self):
        empty_book = {"title": "Empty", "clean_text": "", "chapters": [], "verses": []}
        result = analyze_sentiment(empty_book)
        assert "error" in result
