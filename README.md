# 🏛️ Gutenberg Ebook Analysis Engine

A comprehensive computational literary and philosophical corpus analysis platform inspired by [QuranAnalysis.com](https://qurananalysis.com/), tailored for Friedrich Nietzsche's works and any Project Gutenberg ebook or custom text.

---

## 🌟 Key Features

### 📊 Corpus Analytics
- **Basic Statistics**: Word counts, type-token ratio (TTR), Hapax Legomena, readability indices (Flesch-Kincaid, Gunning Fog, Flesch Reading Ease), sentence length distributions.
- **Word Frequency & TF-IDF**: Term frequency, POS tagging, inverse document frequency across chapters, and relative frequency per 10k words.
- **Word Clouds**: Visual high-density thematic word clouds.
- **Charts & Distributions**: Interactive Chart.js charts for word frequency, POS distributions, and chapter progression.

### 🧩 Syntax & Patterns
- **N-Grams Explorer**: 2-gram to 5-gram multi-word phrase discovery with context snippets and stopword filtering.
- **PoS Patterns & Sequences**: Frequent grammatical patterns (e.g. `ADJ NOUN`, `PRON VERB ADV`).
- **PoS Query Engine**: Search verses matching exact grammatical formulas with real-time highlighted matches.

### 🔁 Structure & Repetitions
- **Repeated Verses**: Exact duplicate passages and fuzzy near-duplicate matching (Jaccard token similarity) for recurring refrains.
- **Repeated Phrases**: Recurring multi-word idioms and aphoristic formulas.
- **Pause Marks & Rhetorical Cadence**: Punctuation density (Em-dashes, Exclamations, Semicolons, Interrogatives) and aphoristic rhythm metrics.

### 🕸️ Semantics & Ontology
- **Ontology Data & Graphs**: Curated philosophical taxonomies (Will to Power, Übermensch, Eternal Recurrence, Apollonian/Dionysian, Master-Slave Morality, Nihilism) with interactive Vis.js force-directed knowledge graphs.
- **Word Information / Lexicon Profile**: Detailed linguistic profile: lemma, syllables, corpus rank, POS breakdown, collocates, and context passages.
- **Collocations**: Statistical word pairings scored by Pointwise Mutual Information (PMI), NPMI, and T-Scores.
- **Concordance (KWIC)**: Key Word in Context aligner supporting single words, multi-word phrases, and `regex:` prefix patterns.
- **Word Similarity**: Memory-efficient sparse matrix PPMI co-occurrence vector spaces and cosine similarity.

### 🎭 Advanced Analysis (New)
- **Sentiment Analysis**: VADER-based per-chapter emotional arcs, polarity trajectories, and most impassioned passages.
- **Compare Books**: Side-by-side comparative analysis of vocabulary overlap (Jaccard similarity), unique exclusive terms, readability differences, and concept densities.
- **Full-Text Search**: Instant search for any word, phrase, or regular expression across all segmented verses.

### 💾 Export & UX
- **Dataset Export**: One-click export to CSV, JSON, or full analytics bundles.
- **Modern Responsive Web UI**: Glassmorphic dark/light themes, mobile hamburger navigation, skeleton loading states, and persistent local bookmarks.
- **Keyboard Shortcuts**: `1-5` for direct tab switching, `Ctrl+K` for command palette, `Ctrl+B` for bookmarks panel.

---

## 🚀 Quick Start

### 1. Requirements & Installation
The project uses `uv` for modern Python package management:

```bash
git clone https://github.com/nichsedge/gutenberg.git
cd gutenberg

# Install dependencies and download NLTK data
uv sync
```

### 2. Launch Interactive Web Dashboard
```bash
uv run main.py --server
# Or using the script entry point:
uv run gutenberg --server

# Open http://localhost:8455
```

### 3. CLI Analysis Commands
```bash
# Basic Statistics
uv run main.py --stats --book 1998

# Top Word Frequencies & TF-IDF
uv run main.py --freq --book 1998

# Philosophical Ontology
uv run main.py --ontology --book 1998

# KWIC Concordance
uv run main.py --concordance zarathustra --book 1998

# Pause Marks & Rhetorical Rhythm
uv run main.py --pauses --book 1998

# Semantic Vector Similarity
uv run main.py --similarity power --book 1998
```

---

## 🧪 Testing

Run the full pytest suite:

```bash
uv run pytest tests/ -v
```

---

## 📡 REST API Reference

All endpoints return JSON and are non-blocking:

| Endpoint | Method | Description |
|---|---|---|
| `/api/catalog` | GET | List available and cached books |
| `/api/stats?book_id={id}` | GET | Basic corpus statistics and readability |
| `/api/frequency?book_id={id}` | GET | Word frequencies and TF-IDF weights |
| `/api/sentiment?book_id={id}` | GET | Chapter-level sentiment arcs & polarity |
| `/api/compare?book_id_a={a}&book_id_b={b}` | GET | Cross-book vocabulary & style comparison |
| `/api/search?book_id={id}&phrase={q}` | GET | Full-text verse search with highlighting |
| `/api/concordance?book_id={id}&keyword={k}` | GET | KWIC concordance alignments |
| `/api/collocation?book_id={id}` | GET | Word collocation metrics (PMI / T-Score) |
| `/api/similarity?book_id={id}&word1={w}` | GET | Nearest semantic neighbors via PPMI |
| `/api/export?book_id={id}&format_type={csv\|json}` | GET | Download structured corpus datasets |

---

## 📜 License
MIT License
