"""
Book parser: fetch from Project Gutenberg or load local EPUB/TXT files.
Uses pathlib.Path throughout. Default author for unknown books is 'Unknown'.
"""
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

import requests
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub

logger = logging.getLogger(__name__)

# Curated catalog of classic literature and philosophy on Project Gutenberg
FEATURED_CATALOG = {
    "1342": {
        "id": "1342",
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "year": "1813",
        "category": "Classic Literature / Romance & Satire",
        "gutenberg_url": "https://www.gutenberg.org/cache/epub/1342/pg1342.txt",
    },
    "84": {
        "id": "84",
        "title": "Frankenstein; Or, The Modern Prometheus",
        "author": "Mary Wollstonecraft Shelley",
        "year": "1818",
        "category": "Gothic Fiction / Science Fiction",
        "gutenberg_url": "https://www.gutenberg.org/cache/epub/84/pg84.txt",
    },
    "11": {
        "id": "11",
        "title": "Alice's Adventures in Wonderland",
        "author": "Lewis Carroll",
        "year": "1865",
        "category": "Children's Literature / Fantasy",
        "gutenberg_url": "https://www.gutenberg.org/cache/epub/11/pg11.txt",
    },
    "2701": {
        "id": "2701",
        "title": "Moby Dick; or, The Whale",
        "author": "Herman Melville",
        "year": "1851",
        "category": "Adventure / Philosophical Fiction",
        "gutenberg_url": "https://www.gutenberg.org/cache/epub/2701/pg2701.txt",
    },
    "1661": {
        "id": "1661",
        "title": "The Adventures of Sherlock Holmes",
        "author": "Arthur Conan Doyle",
        "year": "1892",
        "category": "Mystery / Detective Fiction",
        "gutenberg_url": "https://www.gutenberg.org/cache/epub/1661/pg1661.txt",
    },
    "174": {
        "id": "174",
        "title": "The Picture of Dorian Gray",
        "author": "Oscar Wilde",
        "year": "1890",
        "category": "Philosophical Fiction / Gothic",
        "gutenberg_url": "https://www.gutenberg.org/cache/epub/174/pg174.txt",
    },
    "1497": {
        "id": "1497",
        "title": "The Republic",
        "author": "Plato",
        "year": "c. 375 BC",
        "category": "Classical Philosophy / Political Philosophy",
        "gutenberg_url": "https://www.gutenberg.org/cache/epub/1497/pg1497.txt",
    },
    "1998": {
        "id": "1998",
        "title": "Thus Spake Zarathustra",
        "author": "Friedrich Wilhelm Nietzsche",
        "year": "1883-1885",
        "category": "Philosophy / Aphorism",
        "gutenberg_url": "https://www.gutenberg.org/cache/epub/1998/pg1998.txt",
    },
    "4363": {
        "id": "4363",
        "title": "Beyond Good and Evil",
        "author": "Friedrich Wilhelm Nietzsche",
        "year": "1886",
        "category": "Philosophy / Critique of Morality",
        "gutenberg_url": "https://www.gutenberg.org/cache/epub/4363/pg4363.txt",
    },
    "5200": {
        "id": "5200",
        "title": "Metamorphosis",
        "author": "Franz Kafka",
        "year": "1915",
        "category": "Modernist Fiction / Absurdist",
        "gutenberg_url": "https://www.gutenberg.org/cache/epub/5200/pg5200.txt",
    },
}
NIETZSCHE_CATALOG = FEATURED_CATALOG


class BookParser:
    def __init__(self, cache_dir: str = "data/books"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_catalog(self) -> List[Dict[str, Any]]:
        """Return list of curated + locally cached books."""
        catalog = list(FEATURED_CATALOG.values())
        for p in self.cache_dir.iterdir():
            if p.suffix in {".txt", ".epub"}:
                book_id = p.stem.removeprefix("pg")
                if book_id not in FEATURED_CATALOG:
                    catalog.append({
                        "id": book_id,
                        "title": f"Custom Book ({p.name})",
                        "author": "Unknown",
                        "year": "N/A",
                        "category": "Custom Upload",
                        "gutenberg_url": "",
                    })
        return catalog

    def fetch_or_load_book(self, book_id_or_path: str) -> Dict[str, Any]:
        """Load book from disk or download from Project Gutenberg."""
        path = Path(book_id_or_path)
        if path.is_file():
            return self._parse_file(path)

        book_id = str(book_id_or_path).strip()
        cache_txt = self.cache_dir / f"pg{book_id}.txt"
        cache_epub = self.cache_dir / f"pg{book_id}.epub"

        if cache_txt.is_file():
            return self._parse_file(cache_txt, book_id=book_id)
        if cache_epub.is_file():
            return self._parse_file(cache_epub, book_id=book_id)

        # Download from Gutenberg
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        urls_to_try = [
            f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt",
            f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
            f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt",
        ]

        for url in urls_to_try:
            try:
                resp = requests.get(url, headers=headers, timeout=20)
                if resp.status_code == 200 and len(resp.content) > 1000:
                    text_content = resp.content.decode("utf-8", errors="replace")
                    cache_txt.write_text(text_content, encoding="utf-8")
                    return self._parse_text(text_content, book_id=book_id)
            except Exception as e:
                logger.warning(f"Failed to download from {url}: {e}")

        raise ValueError(f"Could not load or download book for '{book_id_or_path}'.")

    def _parse_file(self, file_path: Path, book_id: Optional[str] = None) -> Dict[str, Any]:
        if file_path.suffix == ".epub":
            return self._parse_epub(file_path, book_id)
        text = file_path.read_text(encoding="utf-8", errors="replace")
        return self._parse_text(text, book_id=book_id, source_path=file_path)

    def _parse_epub(self, file_path: Path, book_id: Optional[str] = None) -> Dict[str, Any]:
        book = epub.read_epub(str(file_path))
        title_meta = book.get_metadata("DC", "title")
        title_str = title_meta[0][0] if title_meta else file_path.stem
        creator_meta = book.get_metadata("DC", "creator")
        author_str = creator_meta[0][0] if creator_meta else "Unknown"

        full_text: List[str] = []
        chapters: List[Dict[str, Any]] = []
        chap_num = 1

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content().decode("utf-8", errors="replace"), "html.parser")
                text = soup.get_text()
                clean = re.sub(r"\s+", " ", text).strip()
                if len(clean) > 80:
                    full_text.append(clean)
                    chapters.append({"id": chap_num, "title": f"Chapter {chap_num}", "text": clean})
                    chap_num += 1

        raw_text = "\n\n".join(full_text)
        return self._build_book_structure(
            raw_text=raw_text,
            clean_text=raw_text,
            title=title_str,
            author=author_str,
            book_id=book_id or "epub",
            chapters=chapters,
        )

    def _strip_gutenberg_headers(self, text: str) -> str:
        start_match = re.search(
            r"\*\*\*\s*START OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", text, re.IGNORECASE
        )
        if start_match:
            text = text[start_match.end():]
        end_match = re.search(
            r"\*\*\*\s*END OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", text, re.IGNORECASE
        )
        if end_match:
            text = text[: end_match.start()]
        return text.strip()

    def _extract_metadata(self, text: str, book_id: Optional[str]) -> Dict[str, str]:
        if book_id and book_id in FEATURED_CATALOG:
            meta = FEATURED_CATALOG[book_id]
            return {"title": meta["title"], "author": meta["author"], "year": meta.get("year", "")}

        title = "Unknown Work"
        author = "Unknown"

        title_match = re.search(r"Title:\s*(.+)", text, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()

        author_match = re.search(r"Author:\s*(.+)", text, re.IGNORECASE)
        if author_match:
            author = author_match.group(1).strip()

        return {"title": title, "author": author, "year": "N/A"}

    def _parse_text(
        self, text: str, book_id: Optional[str] = None, source_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        meta = self._extract_metadata(text, book_id)
        clean_text = self._strip_gutenberg_headers(text)
        chapters = self._segment_into_chapters(clean_text)
        fallback_id = source_path.stem if source_path else "1998"

        return self._build_book_structure(
            raw_text=text,
            clean_text=clean_text,
            title=meta["title"],
            author=meta["author"],
            book_id=book_id or fallback_id,
            chapters=chapters,
        )

    def _segment_into_chapters(self, text: str) -> List[Dict[str, Any]]:
        chapter_pattern = re.compile(
            r"(?:^|\n\n+)(?:(?:CHAPTER|PART|SECTION|DISCOURSE|BOOK|APHORISM)\s+"
            r"([IVXLCDM0-9]+|\w+)|([IVXLCDM]+\.)|([0-9]+\.))\s*([^\n]*)",
            re.IGNORECASE,
        )

        matches = list(chapter_pattern.finditer(text))
        if len(matches) >= 3:
            chapters = []
            for i, match in enumerate(matches):
                start = match.start()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                chap_header = match.group(0).strip()
                chap_title = chap_header.split("\n")[0][:80]
                chap_body = text[start:end].strip()
                if len(chap_body) > 50:
                    chapters.append({"id": i + 1, "title": chap_title, "text": chap_body})
            if chapters:
                return chapters

        # Fallback: fixed-size word chunks
        words = text.split()
        chunk_size = 1500
        chapters = []
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i: i + chunk_size]
            chap_num = (i // chunk_size) + 1
            sample_title = " ".join(chunk_words[:5]) + "..."
            chapters.append({
                "id": chap_num,
                "title": f"Section {chap_num}: {sample_title}",
                "text": " ".join(chunk_words),
            })
        return chapters

    def _build_book_structure(
        self,
        raw_text: str,
        clean_text: str,
        title: str,
        author: str,
        book_id: str,
        chapters: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        verses: List[Dict[str, Any]] = []
        verse_idx = 1

        for chap in chapters:
            chap_id = chap["id"]
            chap_title = chap["title"]
            paras = [p.strip() for p in re.split(r"(?:\r?\n\s*){2,}", chap["text"]) if p.strip()]
            if len(paras) <= 1:
                from analyzer.nltk_helper import tokenize_sentences
                paras = tokenize_sentences(chap["text"])

            for p_num, para in enumerate(paras, 1):
                clean_para = re.sub(r"\s+", " ", para)
                if len(clean_para) > 10:
                    verses.append({
                        "id": verse_idx,
                        "chapter_id": chap_id,
                        "chapter_title": chap_title,
                        "verse_num": p_num,
                        "text": clean_para,
                        "word_count": len(clean_para.split()),
                    })
                    verse_idx += 1

        return {
            "id": book_id,
            "title": title,
            "author": author,
            "raw_text": raw_text,
            "clean_text": clean_text,
            "total_characters": len(clean_text),
            "chapters": chapters,
            "verses": verses,
            "total_chapters": len(chapters),
            "total_verses": len(verses),
        }
