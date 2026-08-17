"""
Shared test fixtures for the Gutenberg ebook analysis test suite.
"""
import pytest

# A short self-contained philosophical text (~150 words) used across all test modules
FIXTURE_TEXT = """
Thus spoke Zarathustra: Man is a rope stretched between the animal and the Superman.
What is great in man is that he is a bridge and not a goal.
I love those who do not know how to live, for they are the ones who cross over.
The higher we soar, the smaller we appear to those who cannot fly.
Without music, life would be a mistake. And those who were seen dancing were thought to
be insane by those who could not hear the music.
That which does not kill us makes us stronger. One must still have chaos in oneself to
be able to give birth to a dancing star.
God is dead. And we have killed him. How shall we comfort ourselves, the murderers of
all murderers? What was holiest and most powerful of all that the world has yet owned
has bled to death under our knives. Who will wipe this blood off us?
The secret for harvesting from existence the greatest fruitfulness and the greatest
enjoyment is to live dangerously. Build your cities on the slopes of Vesuvius!
"""

FIXTURE_BOOK = {
    "id": "test_fixture",
    "title": "Fixture Thus Spoke Zarathustra",
    "author": "Friedrich Nietzsche",
    "raw_text": FIXTURE_TEXT,
    "clean_text": FIXTURE_TEXT,
    "total_characters": len(FIXTURE_TEXT),
    "chapters": [
        {"id": 1, "title": "Chapter One", "text": FIXTURE_TEXT[:len(FIXTURE_TEXT)//2]},
        {"id": 2, "title": "Chapter Two", "text": FIXTURE_TEXT[len(FIXTURE_TEXT)//2:]},
    ],
    "verses": [
        {"id": i + 1, "chapter_id": 1 if i < 4 else 2, "chapter_title": "Chapter One" if i < 4 else "Chapter Two",
         "verse_num": i + 1, "text": s.strip(), "word_count": len(s.split())}
        for i, s in enumerate([
            "Man is a rope stretched between the animal and the Superman.",
            "What is great in man is that he is a bridge and not a goal.",
            "I love those who do not know how to live for they are the ones who cross over.",
            "The higher we soar the smaller we appear to those who cannot fly.",
            "Without music life would be a mistake.",
            "That which does not kill us makes us stronger.",
            "God is dead. And we have killed him.",
            "The secret for harvesting from existence the greatest fruitfulness is to live dangerously.",
        ])
    ],
    "total_chapters": 2,
    "total_verses": 8,
}


@pytest.fixture
def fixture_book():
    return FIXTURE_BOOK


@pytest.fixture
def fixture_text():
    return FIXTURE_TEXT
