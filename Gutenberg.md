# Ebook Analysis

A comprehensive computational literary and philosophical corpus analysis platform inspired by [QuranAnalysis.com](https://qurananalysis.com/), tailored for Friedrich Nietzsche's works and any Project Gutenberg ebook or custom text.

## Features & Implementation Status

- [x] **Basic Statistics** (`analyzer/basic_stats.py`): Word counts, vocabulary richness (TTR, Hapax Legomena), character stats, readability scores (Flesch-Kincaid, Gunning Fog), word length distributions.
- [x] **Word Frequency & TF-IDF** (`analyzer/frequency.py`): Term frequency, inverse document frequency across chapters, relative frequencies per 10k words, POS tags, stopword filtering.
- [x] **Word Clouds** (`analyzer/wordcloud_gen.py`): High-resolution word cloud generation and dynamic weight extraction.
- [x] **Charts & Distributions** (`web/static/app.js`): Interactive Chart.js visual distributions for top words, POS breakdown, and chapter progress.
- [x] **N-Grams** (`analyzer/ngrams.py`): 2-gram, 3-gram, 4-gram, 5-gram extraction with context snippets and filtering.
- [x] **PoS Patterns** (`analyzer/pos_analyzer.py`): Discover common grammatical Part-of-Speech sequences (e.g. `ADJ NOUN`, `PRON VERB ADV`).
- [x] **PoS Query** (`analyzer/pos_analyzer.py`): Search verses and aphorisms matching custom grammatical POS sequences with real-time highlighted matches.
- [x] **Repeated Verses** (`analyzer/repetition.py`): Exact duplicate passages and fuzzy near-duplicate matching (Jaccard similarity) for recurring refrains.
- [x] **Repeated Phrases / Common Substrings** (`analyzer/repetition.py`): Multi-word recurring idioms and aphoristic formulas.
- [x] **Ontology Data** (`analyzer/ontology.py`): Philosophical taxonomy (Will to Power, Übermensch, Eternal Recurrence, Apollonian/Dionysian, Master-Slave Morality, Nihilism, etc.).
- [x] **Ontology Graphs** (`web/static/app.js` & `analyzer/ontology.py`): Interactive Vis.js Force-Directed Network Graph of concept co-occurrences.
- [x] **Word Information / Lexicon** (`analyzer/word_info.py`): Full linguistic profile for any word: lemma, syllables, rank, POS breakdown, collocates, and context passages.
- [x] **Collocation** (`analyzer/collocation.py`): Word co-occurrence affinities scored by Pointwise Mutual Information (PMI), NPMI, and T-Scores.
- [x] **Concordance (KWIC)** (`analyzer/concordance.py`): Key Word In Context explorer with left/right context columns and sorting.
- [x] **Pause Marks & Rhetorical Cadence** (`analyzer/pause_marks.py`): Punctuation density (Em-dashes, Exclamations, Semicolons, Interrogatives) and aphoristic rhythm metrics.
- [x] **Word Similarity** (`analyzer/similarity.py`): Semantic vector similarity, cosine distance, and nearest conceptual neighbors.
- [x] **To Dataset** (`analyzer/dataset_exporter.py`): One-click export to CSV, JSON bundle, and programmatic REST API.

## Quick Start

### Launch Web Dashboard
```bash
uv run main.py --server
# Open http://localhost:8000
```

### CLI Analysis Commands
```bash
# Basic Statistics
uv run main.py --stats --book 1998

# Top Word Frequencies & TF-IDF
uv run main.py --freq --book 1998

# Philosophical Ontology
uv run main.py --ontology --book 1998

# KWIC Concordance for a keyword
uv run main.py --concordance zarathustra --book 1998

# Pause Marks & Rhetorical Rhythm
uv run main.py --pauses --book 1998

# Semantic Vector Similarity
uv run main.py --similarity power --book 1998
```
