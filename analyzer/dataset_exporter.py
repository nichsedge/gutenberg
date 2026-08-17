import io
import json
import csv
from typing import Dict, Any, List
import pandas as pd
from analyzer.basic_stats import calculate_basic_statistics
from analyzer.frequency import calculate_word_frequencies
from analyzer.ontology import extract_ontology_data

def export_book_dataset(book_data: Dict[str, Any], format_type: str = "json") -> Any:
    """
    Export ebook analysis and structured corpus to JSON, CSV, or DataFrame.
    """
    verses = book_data.get("verses", [])
    
    # 1. Verses Dataset
    verse_records = []
    for v in verses:
        verse_records.append({
            "book_id": book_data.get("id", ""),
            "book_title": book_data.get("title", ""),
            "author": book_data.get("author", ""),
            "chapter_id": v.get("chapter_id", 1),
            "chapter_title": v.get("chapter_title", ""),
            "verse_id": v.get("id", 1),
            "text": v.get("text", ""),
            "word_count": v.get("word_count", 0)
        })

    df = pd.DataFrame(verse_records)

    if format_type == "csv":
        return df.to_csv(index=False)
    elif format_type == "json":
        return json.dumps({
            "metadata": {
                "id": book_data.get("id"),
                "title": book_data.get("title"),
                "author": book_data.get("author"),
                "total_verses": len(verses),
                "total_chapters": len(book_data.get("chapters", []))
            },
            "verses": verse_records
        }, indent=2)
    elif format_type == "full_bundle":
        # Full bundled analytics dataset
        stats = calculate_basic_statistics(book_data)
        freq = calculate_word_frequencies(book_data, limit=300)
        ontology = extract_ontology_data(book_data)
        return json.dumps({
            "metadata": {
                "id": book_data.get("id"),
                "title": book_data.get("title"),
                "author": book_data.get("author")
            },
            "statistics": stats,
            "top_frequencies": freq.get("frequencies", []),
            "ontology": ontology.get("concepts", []),
            "verses": verse_records
        }, indent=2)
    else:
        return df
