# 🏛️ Gutenberg Ebook Analysis Engine

A comprehensive computational literary and corpus analysis platform inspired by [QuranAnalysis.com](https://qurananalysis.com/), built for analyzing **any book or text from Project Gutenberg**, custom EPUB, or TXT file.

Explore classic literature, philosophy, drama, and essays—from Jane Austen, Mary Shelley, and Lewis Carroll to Herman Melville, Friedrich Nietzsche, Franz Kafka, and Plato—or fetch any Project Gutenberg ID directly on the fly.

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
- **Repeated Verses & Passages**: Exact duplicate passages and fuzzy near-duplicate matching (Jaccard token similarity) for recurring refrains.
- **Repeated Phrases**: Recurring multi-word idioms and stylistic formulas.
- **Pause Marks & Rhetorical Cadence**: Punctuation density (Em-dashes, Exclamations, Semicolons, Interrogatives) and syntactic rhythm metrics.

### 🕸️ Semantics & Ontology
- **Conceptual & Thematic Ontology**: Curated philosophical and literary taxonomies with interactive Vis.js force-directed knowledge graphs.
- **Word Information / Lexicon Profile**: Detailed linguistic profile: lemma, syllables, corpus rank, POS breakdown, collocates, and context passages.
- **Collocations**: Statistical word pairings scored by Pointwise Mutual Information (PMI), NPMI, and T-Scores.
- **Concordance (KWIC)**: Key Word in Context aligner supporting single words, multi-word phrases, and `regex:` prefix patterns.
- **Word Similarity**: Memory-efficient sparse matrix PPMI co-occurrence vector spaces and cosine similarity.

### 🎭 Comparative & Advanced Analysis
- **Sentiment Analysis**: VADER-based per-chapter emotional arcs, polarity trajectories, and most impassioned passages.
- **Compare Books**: Side-by-side comparative analysis of vocabulary overlap (Jaccard similarity), unique exclusive terms, readability differences, and concept densities.
- **Full-Text Search**: Instant search for any word, phrase, or regular expression across all segmented passages.

### 💾 Universal Ingestion & Export
- **Any Gutenberg Book on Demand**: Enter any Project Gutenberg book ID (e.g. `1342`, `84`, `11`, `2701`, `1998`) to automatically download, clean headers, and analyze.
- **Custom Uploads**: Supports loading local `.epub` and `.txt` files.
- **Dataset Export**: One-click export to CSV, JSON, or full analytics bundles.
- **Modern Responsive Web UI**: Glassmorphic dark/light themes, mobile navigation, skeleton loading states, and persistent local bookmarks.

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
Analyze any book by Project Gutenberg ID or local path:

```bash
# Basic Statistics (e.g. Pride and Prejudice - 1342)
uv run main.py --stats --book 1342

# Top Word Frequencies & TF-IDF (e.g. Frankenstein - 84)
uv run main.py --freq --book 84

# Conceptual & Thematic Ontology (e.g. Thus Spake Zarathustra - 1998)
uv run main.py --ontology --book 1998

# KWIC Concordance for a term (e.g. Alice in Wonderland - 11)
uv run main.py --concordance rabbit --book 11

# Pause Marks & Rhetorical Rhythm (e.g. Moby Dick - 2701)
uv run main.py --pauses --book 2701

# Semantic Vector Similarity
uv run main.py --similarity monster --book 84
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
| `/api/search?book_id={id}&phrase={q}` | GET | Full-text passage search with highlighting |
| `/api/concordance?book_id={id}&keyword={k}` | GET | KWIC concordance alignments |
| `/api/collocation?book_id={id}` | GET | Word collocation metrics (PMI / T-Score) |
| `/api/similarity?book_id={id}&word1={w}` | GET | Nearest semantic neighbors via PPMI |
| `/api/export?book_id={id}&format_type={csv\|json}` | GET | Download structured corpus datasets |

---

## 📜 License
MIT License
