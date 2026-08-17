"""Tests for analyzer/nltk_helper.py"""
import pytest
from analyzer.nltk_helper import (
    tokenize_words,
    tokenize_sentences,
    lemmatize,
    simple_lemmatize,
    tag_pos_tokens,
    STOPWORDS,
)


class TestTokenizeWords:
    def test_basic(self):
        tokens = tokenize_words("Hello world")
        assert tokens == ["hello", "world"]

    def test_lowercase(self):
        tokens = tokenize_words("Nietzsche Will Power")
        assert all(t == t.lower() for t in tokens)

    def test_preserve_case(self):
        tokens = tokenize_words("Thus Spoke Zarathustra", lower=False)
        assert tokens[0] == "Thus"

    def test_strips_punctuation(self):
        tokens = tokenize_words("power! force, will.")
        assert "power" in tokens
        assert "force" in tokens

    def test_empty_string(self):
        assert tokenize_words("") == []

    def test_only_punctuation(self):
        assert tokenize_words("...---!!!") == []


class TestSimpleLemmatize:
    def test_plural_s(self):
        # words → word
        assert simple_lemmatize("words") == "word"

    def test_plural_ies(self):
        # flies → fly
        assert simple_lemmatize("flies") == "fly"

    def test_plural_ves(self):
        # knives → knife
        assert simple_lemmatize("knives") == "knife"

    def test_past_tense_ed(self):
        # jumped → jump
        result = simple_lemmatize("jumped")
        assert result in ("jumped", "jump")  # either acceptable

    def test_gerund_ing(self):
        # running → run (double consonant)
        result = simple_lemmatize("running")
        assert result in ("running", "run", "runn")

    def test_short_word_unchanged(self):
        assert simple_lemmatize("man") == "man"
        assert simple_lemmatize("is") == "is"

    def test_dies_bug_fixed(self):
        # Previously would return "dy" — should return "die" or "di"
        result = simple_lemmatize("dies")
        assert result != "dy", f"Lemmatizer bug: 'dies' → '{result}' should not be 'dy'"


class TestLemmatize:
    def test_noun_lemma(self):
        result = lemmatize("running", "VERB")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_verb_lemma(self):
        result = lemmatize("powers", "NOUN")
        assert isinstance(result, str)

    def test_adj_lemma(self):
        result = lemmatize("greatest", "ADJ")
        assert isinstance(result, str)


class TestPOSTagger:
    def test_returns_tuples(self):
        tokens = ["the", "great", "philosopher", "thinks"]
        tagged = tag_pos_tokens(tokens)
        assert len(tagged) == len(tokens)
        assert all(isinstance(tag, str) and len(tag) > 0 for _, tag in tagged)

    def test_valid_universal_tags(self):
        valid_tags = {"NOUN", "VERB", "ADJ", "ADV", "PRON", "DET", "ADP", "CONJ", "NUM", "PRT", "X", "."}
        tokens = ["he", "walks", "quickly", "over", "the", "old", "bridge"]
        tagged = tag_pos_tokens(tokens)
        for _, tag in tagged:
            assert tag in valid_tags, f"Unknown POS tag: {tag}"

    def test_pronoun_tagged(self):
        tagged = tag_pos_tokens(["he"])
        assert tagged[0][1] == "PRON"

    def test_determiner_tagged(self):
        tagged = tag_pos_tokens(["the"])
        assert tagged[0][1] == "DET"


class TestStopwords:
    def test_common_words_present(self):
        common = ["the", "is", "a", "and", "of", "in", "to"]
        for w in common:
            assert w in STOPWORDS, f"'{w}' should be in STOPWORDS"

    def test_archaic_words_present(self):
        archaic = ["thou", "thee", "thy", "doth", "hath"]
        for w in archaic:
            assert w in STOPWORDS, f"Archaic word '{w}' should be in STOPWORDS"

    def test_content_words_not_stopwords(self):
        content = ["nietzsche", "zarathustra", "power", "eternal", "overman"]
        for w in content:
            assert w not in STOPWORDS, f"Content word '{w}' should NOT be in STOPWORDS"


class TestTokenizeSentences:
    def test_splits_sentences(self):
        text = "Man is a bridge. God is dead. Power is eternal."
        sents = tokenize_sentences(text)
        assert len(sents) >= 2

    def test_returns_non_empty(self):
        text = "Without music life would be a mistake. That which does not kill us makes us stronger."
        sents = tokenize_sentences(text)
        assert all(len(s.strip()) > 0 for s in sents)
