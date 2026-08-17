"""
FastAPI web server for the Gutenberg Ebook Analysis Platform.
All CPU-heavy endpoints run in asyncio.to_thread() to avoid blocking the event loop.
Error handling distinguishes user input errors (400) from bugs (500).
"""
import asyncio
import logging
import os
from typing import Optional

from fastapi import FastAPI, Query, UploadFile, File, Form, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from analyzer.engine import EbookAnalysisEngine

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")

app = FastAPI(
    title="Gutenberg Ebook Analysis Engine",
    description="Comprehensive Computational Literary & Corpus Analysis Platform",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = EbookAnalysisEngine(cache_dir="data/books")

os.makedirs("web/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="web/static"), name="static")


# ── Error helpers ──────────────────────────────────────────────────────────────

def _user_error(e: Exception) -> HTTPException:
    """Map ValueError/FileNotFoundError to 400; everything else to 500."""
    if isinstance(e, (ValueError, KeyError, FileNotFoundError)):
        raise HTTPException(status_code=400, detail=str(e))
    logger.exception("Unexpected server error")
    raise HTTPException(status_code=500, detail=f"Internal error: {type(e).__name__}: {e}")


# ── Static / index ─────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("web/static/index.html", "r", encoding="utf-8") as f:
        return f.read()


# ── Catalog & book loading ─────────────────────────────────────────────────────

@app.get("/api/catalog")
async def get_catalog():
    return {"catalog": await asyncio.to_thread(engine.get_catalog)}


@app.post("/api/load-book")
async def load_book(
    book_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    try:
        if file and file.filename:
            file_path = os.path.join("data/books", file.filename)
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            book = await asyncio.to_thread(engine.parser.fetch_or_load_book, file_path)
            engine._book_cache[book["id"]] = book
            return {"status": "success", "book": {"id": book["id"], "title": book["title"], "author": book["author"]}}
        elif book_id:
            book = await asyncio.to_thread(engine.get_book, book_id)
            return {"status": "success", "book": {"id": book["id"], "title": book["title"], "author": book["author"]}}
        else:
            raise ValueError("Provide a Gutenberg Book ID or upload an EPUB/TXT file.")
    except HTTPException:
        raise
    except Exception as e:
        _user_error(e)


# ── Analysis endpoints ─────────────────────────────────────────────────────────

@app.get("/api/stats")
async def get_stats(book_id: str = Query("1998")):
    try:
        return await asyncio.to_thread(engine.get_basic_stats, book_id)
    except Exception as e:
        _user_error(e)


@app.get("/api/frequency")
async def get_frequency(
    book_id: str = Query("1998"),
    filter_stopwords: bool = Query(True),
    min_length: int = Query(2),
    pos_filter: Optional[str] = Query(None),
    search_query: Optional[str] = Query(None),
    limit: int = Query(500),
):
    try:
        return await asyncio.to_thread(
            engine.get_frequency, book_id, filter_stopwords, min_length, pos_filter, search_query, limit
        )
    except Exception as e:
        _user_error(e)


@app.get("/api/wordcloud")
async def get_wordcloud(book_id: str = Query("1998"), max_words: int = Query(120)):
    try:
        return await asyncio.to_thread(engine.get_wordcloud, book_id, max_words)
    except Exception as e:
        _user_error(e)


@app.get("/api/ngrams")
async def get_ngrams(
    book_id: str = Query("1998"),
    n: int = Query(2),
    filter_stopwords: bool = Query(False),
    min_count: int = Query(2),
    search_query: Optional[str] = Query(None),
    limit: int = Query(200),
):
    try:
        return await asyncio.to_thread(
            engine.get_ngrams, book_id, n, filter_stopwords, min_count, search_query, limit
        )
    except Exception as e:
        _user_error(e)


@app.get("/api/pos-patterns")
async def get_pos_patterns(
    book_id: str = Query("1998"), pattern_length: int = Query(2), limit: int = Query(50)
):
    try:
        return await asyncio.to_thread(engine.get_pos_patterns, book_id, pattern_length, limit)
    except Exception as e:
        _user_error(e)


@app.get("/api/pos-query")
async def query_pos(
    book_id: str = Query("1998"), query: str = Query("ADJ NOUN"), limit: int = Query(100)
):
    try:
        return await asyncio.to_thread(engine.query_pos, book_id, query, limit)
    except Exception as e:
        _user_error(e)


@app.get("/api/repeated-verses")
async def get_repeated_verses(
    book_id: str = Query("1998"),
    min_similarity: float = Query(0.8),
    min_words: int = Query(4),
    limit: int = Query(100),
):
    try:
        return await asyncio.to_thread(engine.get_repeated_verses, book_id, min_similarity, min_words, limit)
    except Exception as e:
        _user_error(e)


@app.get("/api/repeated-phrases")
async def get_repeated_phrases(
    book_id: str = Query("1998"),
    min_phrase_len: int = Query(3),
    max_phrase_len: int = Query(10),
    min_occurrences: int = Query(3),
    limit: int = Query(150),
):
    try:
        return await asyncio.to_thread(
            engine.get_repeated_phrases, book_id, min_phrase_len, max_phrase_len, min_occurrences, limit
        )
    except Exception as e:
        _user_error(e)


@app.get("/api/ontology")
async def get_ontology(book_id: str = Query("1998")):
    try:
        return await asyncio.to_thread(engine.get_ontology, book_id)
    except Exception as e:
        _user_error(e)


@app.get("/api/word-info")
async def get_word_info(book_id: str = Query("1998"), word: str = Query("power")):
    try:
        return await asyncio.to_thread(engine.get_word_info, book_id, word)
    except Exception as e:
        _user_error(e)


@app.get("/api/collocation")
async def get_collocation(
    book_id: str = Query("1998"),
    window_size: int = Query(4),
    min_cooccurrences: int = Query(3),
    filter_stopwords: bool = Query(True),
    target_word: Optional[str] = Query(None),
    limit: int = Query(200),
):
    try:
        return await asyncio.to_thread(
            engine.get_collocations, book_id, window_size, min_cooccurrences,
            filter_stopwords, target_word, limit
        )
    except Exception as e:
        _user_error(e)


@app.get("/api/concordance")
async def get_concordance(
    book_id: str = Query("1998"),
    keyword: str = Query("zarathustra"),
    context_words: int = Query(7),
    chapter_filter: Optional[int] = Query(None),
    sort_by: str = Query("order"),
    limit: int = Query(300),
):
    try:
        return await asyncio.to_thread(
            engine.get_concordance, book_id, keyword, context_words, chapter_filter, sort_by, limit
        )
    except Exception as e:
        _user_error(e)


@app.get("/api/pause-marks")
async def get_pause_marks(book_id: str = Query("1998")):
    try:
        return await asyncio.to_thread(engine.get_pause_marks, book_id)
    except Exception as e:
        _user_error(e)


@app.get("/api/similarity")
async def get_similarity(
    book_id: str = Query("1998"),
    word1: str = Query("power"),
    word2: Optional[str] = Query(None),
    top_k: int = Query(15),
):
    try:
        return await asyncio.to_thread(engine.get_similarity, book_id, word1, word2, top_k)
    except Exception as e:
        _user_error(e)


@app.get("/api/sentiment")
async def get_sentiment(book_id: str = Query("1998")):
    try:
        return await asyncio.to_thread(engine.get_sentiment, book_id)
    except Exception as e:
        _user_error(e)


@app.get("/api/compare")
async def get_comparison(
    book_id_a: str = Query("1998"),
    book_id_b: str = Query("4363"),
):
    try:
        return await asyncio.to_thread(engine.get_comparison, book_id_a, book_id_b)
    except Exception as e:
        _user_error(e)


@app.get("/api/search")
async def full_text_search(
    book_id: str = Query("1998"),
    phrase: str = Query("will to power"),
    limit: int = Query(200),
):
    try:
        return await asyncio.to_thread(engine.full_text_search, book_id, phrase, limit)
    except Exception as e:
        _user_error(e)


@app.get("/api/export")
async def export_dataset(book_id: str = Query("1998"), format_type: str = Query("json")):
    try:
        data = await asyncio.to_thread(engine.export_dataset, book_id, format_type)
        if format_type == "csv":
            return Response(
                content=data,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=ebook_dataset_{book_id}.csv"},
            )
        return Response(
            content=data,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=ebook_dataset_{book_id}.json"},
        )
    except Exception as e:
        _user_error(e)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web.server:app", host="0.0.0.0", port=8455, reload=True)
