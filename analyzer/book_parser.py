import os
import re
import json
import logging
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub

logger = logging.getLogger(__name__)

# Curated catalog of Nietzsche's most influential books on Gutenberg
NIETZSCHE_CATALOG = {
    "1998": {
        "id": "1998",
        "title": "Thus Spake Zarathustra",
        "author": "Friedrich Wilhelm Nietzsche",
        "year": "1883-1885",
        "category": "Philosophy / Aphorism",
        "gutenberg_url": "https://www.gutenberg.org/cache/epub/1998/pg1998.txt"
    },
    "4363": {
        "id": "4363",
        "title": "Beyond Good and Evil",
        "author": "Friedrich Wilhelm Nietzsche",
        "year": "1886",
        "category": "Philosophy / Critique of Morality",
        "gutenberg_url": "https://www.gutenberg.org/cache/epub/4363/pg4363.txt"
    },
    "19322": {
        "id": "19322",
        "title": "The Antichrist",
        "author": "Friedrich Wilhelm Nietzsche",
        "year": "1888",
        "category": "Philosophy / Critique of Religion",
        "gutenberg_url": "https://www.gutenberg.org/cache/epub/19322/pg19322.txt"
    },
    "52319": {
        "id": "52319",
        "title": "The Twilight of the Idols",
        "author": "Friedrich Wilhelm Nietzsche",
        "year": "1889",
        "category": "Philosophy / Aphorisms & Polemic",
        "gutenberg_url": "https://www.gutenberg.org/cache/epub/52319/pg52319.txt"
    },
    "38145": {
        "id": "38145",
        "title": "The Genealogy of Morals",
        "author": "Friedrich Wilhelm Nietzsche",
        "year": "1887",
        "category": "Philosophy / Moral Psychology",
        "gutenberg_url": "https://www.gutenberg.org/cache/epub/38145/pg38145.txt"
    },
    "51710": {
        "id": "51710",
        "title": "The Birth of Tragedy",
        "author": "Friedrich Wilhelm Nietzsche",
        "year": "1872",
        "category": "Aesthetics / Greek Tragedy & Culture",
        "gutenberg_url": "https://www.gutenberg.org/cache/epub/51710/pg51710.txt"
    },
    "39855": {
        "id": "39855",
        "title": "Ecce Homo",
        "author": "Friedrich Wilhelm Nietzsche",
        "year": "1888",
        "category": "Autobiography / Philosophy",
        "gutenberg_url": "https://www.gutenberg.org/cache/epub/39855/pg39855.txt"
    },
    "52881": {
        "id": "52881",
        "title": "Human, All Too Human (Part I)",
        "author": "Friedrich Wilhelm Nietzsche",
        "year": "1878",
        "category": "Philosophy / Free Spirit Series",
        "gutenberg_url": "https://www.gutenberg.org/cache/epub/52881/pg52881.txt"
    }
}

class BookParser:
    def __init__(self, cache_dir: str = "data/books"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_catalog(self) -> List[Dict[str, Any]]:
        """Return list of Nietzsche and sample books in catalog."""
        catalog = list(NIETZSCHE_CATALOG.values())
        if os.path.exists(self.cache_dir):
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".txt") or filename.endswith(".epub"):
                    book_id = filename.split(".")[0].replace("pg", "")
                    if book_id not in NIETZSCHE_CATALOG:
                        catalog.append({
                            "id": book_id,
                            "title": f"Custom Book ({filename})",
                            "author": "Unknown",
                            "year": "N/A",
                            "category": "Custom Upload",
                            "gutenberg_url": ""
                        })
        return catalog

    def fetch_or_load_book(self, book_id_or_path: str) -> Dict[str, Any]:
        """Load book from disk or download from Gutenberg."""
        if os.path.isfile(book_id_or_path):
            return self._parse_file(book_id_or_path)

        cache_txt = os.path.join(self.cache_dir, f"pg{book_id_or_path}.txt")
        cache_epub = os.path.join(self.cache_dir, f"pg{book_id_or_path}.epub")
        if os.path.isfile(cache_txt):
            return self._parse_file(cache_txt, book_id=book_id_or_path)
        if os.path.isfile(cache_epub):
            return self._parse_file(cache_epub, book_id=book_id_or_path)

        book_id = str(book_id_or_path).strip()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        urls_to_try = [
            f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt",
            f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
            f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt"
        ]

        text_content = None
        for url in urls_to_try:
            try:
                resp = requests.get(url, headers=headers, timeout=12)
                if resp.status_code == 200 and len(resp.content) > 1000:
                    text_content = resp.content.decode('utf-8', errors='replace')
                    with open(cache_txt, 'w', encoding='utf-8') as f:
                        f.write(text_content)
                    break
            except Exception as e:
                logger.warning(f"Failed to download from {url}: {e}")

        if text_content is not None:
            return self._parse_text(text_content, book_id=book_id)

        raise ValueError(f"Could not load or download book for '{book_id_or_path}'.")

    def _parse_file(self, file_path: str, book_id: Optional[str] = None) -> Dict[str, Any]:
        if file_path.endswith(".epub"):
            return self._parse_epub(file_path, book_id)
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        return self._parse_text(text, book_id=book_id, source_path=file_path)

    def _parse_epub(self, file_path: str, book_id: Optional[str] = None) -> Dict[str, Any]:
        book = epub.read_epub(file_path)
        title = book.get_metadata('DC', 'title')
        title_str = title[0][0] if title else os.path.basename(file_path)
        creator = book.get_metadata('DC', 'creator')
        author_str = creator[0][0] if creator else "Friedrich Nietzsche"

        full_text = []
        chapters = []
        chap_num = 1

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content().decode('utf-8', errors='replace'), 'html.parser')
                text = soup.get_text()
                clean = re.sub(r'\s+', ' ', text).strip()
                if len(clean) > 80:
                    full_text.append(clean)
                    chapters.append({
                        "id": chap_num,
                        "title": f"Chapter {chap_num}",
                        "text": clean
                    })
                    chap_num += 1

        raw_text = "\n\n".join(full_text)
        return self._build_book_structure(
            raw_text=raw_text,
            clean_text=raw_text,
            title=title_str,
            author=author_str,
            book_id=book_id or "epub",
            chapters=chapters
        )

    def _strip_gutenberg_headers(self, text: str) -> str:
        start_match = re.search(r'\*\*\*\s*START OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*', text, re.IGNORECASE)
        if start_match:
            text = text[start_match.end():]

        end_match = re.search(r'\*\*\*\s*END OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*', text, re.IGNORECASE)
        if end_match:
            text = text[:end_match.start()]

        return text.strip()

    def _extract_metadata(self, text: str, book_id: Optional[str]) -> Dict[str, str]:
        title = "Unknown Work"
        author = "Friedrich Nietzsche"

        if book_id and book_id in NIETZSCHE_CATALOG:
            meta = NIETZSCHE_CATALOG[book_id]
            return {"title": meta["title"], "author": meta["author"], "year": meta.get("year", "")}

        title_match = re.search(r'Title:\s*(.+)', text, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()

        author_match = re.search(r'Author:\s*(.+)', text, re.IGNORECASE)
        if author_match:
            author = author_match.group(1).strip()

        return {"title": title, "author": author, "year": "N/A"}

    def _parse_text(self, text: str, book_id: Optional[str] = None, source_path: Optional[str] = None) -> Dict[str, Any]:
        meta = self._extract_metadata(text, book_id)
        clean_text = self._strip_gutenberg_headers(text)
        chapters = self._segment_into_chapters(clean_text)

        return self._build_book_structure(
            raw_text=text,
            clean_text=clean_text,
            title=meta["title"],
            author=meta["author"],
            book_id=book_id or (os.path.basename(source_path) if source_path else "1998"),
            chapters=chapters
        )

    def _segment_into_chapters(self, text: str) -> List[Dict[str, Any]]:
        chapter_pattern = re.compile(
            r'(?:^|\n\n+)(?:(?:CHAPTER|PART|SECTION|DISCOURSE|BOOK|APHORISM)\s+([IVXLCDM0-9]+|\w+)|([IVXLCDM]+\.)|([0-9]+\.))\s*([^\n]*)',
            re.IGNORECASE
        )

        matches = list(chapter_pattern.finditer(text))
        if len(matches) >= 3:
            chapters = []
            for i in range(len(matches)):
                start = matches[i].start()
                end = matches[i+1].start() if i + 1 < len(matches) else len(text)
                chap_header = matches[i].group(0).strip()
                chap_title = chap_header.split('\n')[0][:80]
                chap_body = text[start:end].strip()
                if len(chap_body) > 50:
                    chapters.append({
                        "id": i + 1,
                        "title": chap_title,
                        "text": chap_body
                    })
            if chapters:
                return chapters

        words = text.split()
        chunk_size = 1500
        chapters = []
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i+chunk_size]
            chap_num = (i // chunk_size) + 1
            sample_title = " ".join(chunk_words[:5]) + "..."
            chapters.append({
                "id": chap_num,
                "title": f"Section {chap_num}: {sample_title}",
                "text": " ".join(chunk_words)
            })

        return chapters

    def _build_book_structure(
        self,
        raw_text: str,
        clean_text: str,
        title: str,
        author: str,
        book_id: str,
        chapters: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        verses = []
        verse_idx = 1

        for chap in chapters:
            chap_id = chap["id"]
            chap_title = chap["title"]
            paras = [p.strip() for p in re.split(r'(?:\r?\n\s*){2,}', chap["text"]) if p.strip()]
            if len(paras) <= 1:
                # If no double newlines, split by sentence groups
                from analyzer.nltk_helper import tokenize_sentences
                sents = tokenize_sentences(chap["text"])
                paras = sents

            for p_num, para in enumerate(paras, 1):
                clean_para = re.sub(r'\s+', ' ', para)
                if len(clean_para) > 10:
                    verses.append({
                        "id": verse_idx,
                        "chapter_id": chap_id,
                        "chapter_title": chap_title,
                        "verse_num": p_num,
                        "text": clean_para,
                        "word_count": len(clean_para.split())
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
            "total_verses": len(verses)
        }
