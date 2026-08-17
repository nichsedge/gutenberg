import argparse
import sys
from analyzer.engine import EbookAnalysisEngine

def main():
    parser = argparse.ArgumentParser(description="Ebook Analysis Engine — QuranAnalysis-style literary NLP suite")
    parser.add_argument("--server", action="store_true", help="Launch the interactive web application server")
    parser.add_argument("--port", type=int, default=8455, help="Web server port (default 8455)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Web server host (default 0.0.0.0)")
    parser.add_argument("--book", type=str, default="1998", help="Book ID or path (default 1998: Thus Spake Zarathustra)")
    parser.add_argument("--stats", action="store_true", help="Print Basic Statistics")
    parser.add_argument("--freq", action="store_true", help="Print Top Word Frequencies")
    parser.add_argument("--ontology", action="store_true", help="Print Philosophical Concept Mentions")
    parser.add_argument("--concordance", type=str, help="Generate KWIC concordance for given keyword")
    parser.add_argument("--pauses", action="store_true", help="Analyze Pause Marks and Rhetorical Cadence")
    parser.add_argument("--similarity", type=str, help="Find semantically similar words for target term")

    args = parser.parse_args()

    if args.server or len(sys.argv) == 1:
        import uvicorn
        print(f"🚀 Launching Ebook Analysis Web Server at http://{args.host}:{args.port}")
        uvicorn.run("web.server:app", host=args.host, port=args.port, reload=True)
        return

    engine = EbookAnalysisEngine()

    if args.stats:
        stats = engine.get_basic_stats(args.book)
        print("\n=== BASIC STATISTICS ===")
        print(f"Title: {stats['title']} by {stats['author']}")
        print(f"Total Words: {stats['total_words']:,}")
        print(f"Unique Vocabulary: {stats['unique_words']:,} (TTR: {stats['type_token_ratio']}%)")
        print(f"Total Verses/Aphorisms: {stats['total_verses']:,}")
        print(f"Flesch-Kincaid Grade: {stats['flesch_kincaid_grade']} | Reading Ease: {stats['flesch_reading_ease']}")
        print(f"Estimated Reading Time: {stats['estimated_reading_minutes']} minutes")

    if args.freq:
        freq = engine.get_frequency(args.book, limit=15)
        print("\n=== TOP 15 FREQUENT WORDS ===")
        for f in freq['frequencies']:
            print(f"#{f['rank']:2d} {f['word']:<15} (Count: {f['count']:4d}, POS: {f['pos']}, TF-IDF: {f['tfidf']})")

    if args.ontology:
        ont = engine.get_ontology(args.book)
        print("\n=== PHILOSOPHICAL ONTOLOGY CONCEPTS ===")
        for c in ont['concepts']:
            print(f"• {c['name']:<25} ({c['category']}): {c['frequency']} mentions")

    if args.concordance:
        conc = engine.get_concordance(args.book, args.concordance, limit=10)
        print(f"\n=== CONCORDANCE FOR '{args.concordance}' ({conc['total_matches']} total matches) ===")
        for line in conc['lines']:
            print(f"{line['left_context']:>35} [{line['keyword']}] {line['right_context']}")

    if args.pauses:
        pm = engine.get_pause_marks(args.book)
        print("\n=== PAUSE MARKS & RHETORICAL CADENCE ===")
        for m in pm['marks_breakdown']:
            print(f"• {m['mark']:<24}: {m['count']} (Density: {m['density_per_1000_words']} per 1k words)")

    if args.similarity:
        sim = engine.get_similarity(args.book, args.similarity, top_k=8)
        print(f"\n=== SEMANTICALLY SIMILAR WORDS FOR '{args.similarity}' ===")
        for sw in sim.get('similar_words', []):
            print(f"• {sw['word']:<15} (Similarity: {sw['similarity_score']}%, Cosine: {sw['similarity']})")

if __name__ == "__main__":
    main()
