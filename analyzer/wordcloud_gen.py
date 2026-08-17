import io
import base64
from typing import Dict, Any, List
from collections import Counter
from analyzer.nltk_helper import tokenize_words, STOPWORDS

try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False

def get_wordcloud_data(book_data: Dict[str, Any], max_words: int = 150) -> Dict[str, Any]:
    """Generate wordcloud frequency data and base64 PNG image."""
    words = tokenize_words(book_data["clean_text"])
    filtered_words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    counts = Counter(filtered_words)

    most_common = counts.most_common(max_words)
    if not most_common:
        return {"words": [], "image_base64": None}

    max_count = most_common[0][1] if most_common else 1
    word_list = [
        {"text": word, "size": round((count / max_count) * 60 + 14), "count": count}
        for word, count in most_common
    ]

    image_base64 = None
    if WORDCLOUD_AVAILABLE and len(filtered_words) > 0:
        try:
            wc = WordCloud(
                width=900,
                height=500,
                background_color='#0f172a',
                colormap='amber' if hasattr(plt.cm, 'amber') else 'YlOrBr',
                max_words=max_words,
                random_state=42
            ).generate_from_frequencies(dict(most_common))

            img_buf = io.BytesIO()
            wc.to_image().save(img_buf, format='PNG')
            image_base64 = "data:image/png;base64," + base64.b64encode(img_buf.getvalue()).decode('utf-8')
        except Exception:
            image_base64 = None

    return {
        "words": word_list,
        "image_base64": image_base64
    }
