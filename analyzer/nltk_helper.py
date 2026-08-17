import re
import os
import string
import logging
from typing import List, Tuple, Set

logger = logging.getLogger(__name__)

# ── NLTK bootstrap ────────────────────────────────────────────────────────────
def _ensure_nltk_data() -> bool:
    """Download required NLTK resources if not already present. Returns True if NLTK is usable."""
    try:
        import nltk
        _needed = [
            ("taggers", "averaged_perceptron_tagger_eng"),
            ("corpora", "wordnet"),
            ("tokenizers", "punkt_tab"),
            ("sentiment", "vader_lexicon"),
        ]
        for category, name in _needed:
            try:
                nltk.data.find(f"{category}/{name}")
            except LookupError:
                nltk.download(name, quiet=True)
        return True
    except Exception as e:
        logger.warning(f"NLTK data bootstrap failed: {e}. Falling back to heuristic tagger.")
        return False

NLTK_AVAILABLE: bool = _ensure_nltk_data()

# ── POS tag mapping Penn Treebank → Universal ─────────────────────────────────
_PTB_TO_UNIVERSAL: dict[str, str] = {
    "NN": "NOUN", "NNS": "NOUN", "NNP": "NOUN", "NNPS": "NOUN",
    "VB": "VERB", "VBD": "VERB", "VBG": "VERB", "VBN": "VERB",
    "VBP": "VERB", "VBZ": "VERB", "MD": "VERB",
    "JJ": "ADJ", "JJR": "ADJ", "JJS": "ADJ",
    "RB": "ADV", "RBR": "ADV", "RBS": "ADV", "WRB": "ADV",
    "PRP": "PRON", "PRP$": "PRON", "WP": "PRON", "WP$": "PRON",
    "DT": "DET", "WDT": "DET", "PDT": "DET",
    "IN": "ADP", "TO": "ADP",
    "CC": "CONJ",
    "CD": "NUM",
    "RP": "PRT", "EX": "PRT",
    ".": ".", ",": ".", ":": ".", "``": ".", "''": ".", "(": ".", ")": ".", "-LRB-": ".", "-RRB-": ".",
    "UH": "X", "FW": "X", "SYM": "X", "LS": "X", "POS": "X",
}

def _ptb_to_universal(tag: str) -> str:
    return _PTB_TO_UNIVERSAL.get(tag, "NOUN")

# ── WordNet POS mapping ───────────────────────────────────────────────────────
def _universal_to_wordnet(pos: str) -> str:
    """Map universal POS to WordNet constants."""
    from nltk.corpus import wordnet as wn
    return {
        "NOUN": wn.NOUN,
        "VERB": wn.VERB,
        "ADJ": wn.ADJ,
        "ADV": wn.ADV,
    }.get(pos, wn.NOUN)

# ── Standard English stopwords (including archaic forms for pre-20th-c texts) ─
STOPWORDS: Set[str] = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours",
    "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers",
    "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
    "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does",
    "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until",
    "while", "of", "at", "by", "for", "with", "about", "against", "between", "into",
    "through", "during", "before", "after", "above", "below", "to", "from", "up", "down",
    "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now", "d",
    "ll", "m", "o", "re", "ve", "y", "ain", "aren", "couldn", "didn", "doesn", "hadn",
    "hasn", "haven", "isn", "ma", "mightn", "mustn", "needn", "shan", "shouldn", "wasn",
    "weren", "won", "wouldn",
    # Archaic / KJV English
    "thou", "thee", "thy", "thine", "ye", "unto", "doth", "hath", "art", "shalt",
    "wilt", "hast", "dost", "nay", "yea",
}

# ── Tokenizers ────────────────────────────────────────────────────────────────
WORD_RE = re.compile(r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b")
SENTENCE_RE = re.compile(r'(?<=[.!?])\s+(?=[A-Z""\'\d])')

def tokenize_words(text: str, lower: bool = True) -> List[str]:
    """Tokenize words from text."""
    if lower:
        return [w.lower() for w in WORD_RE.findall(text)]
    return WORD_RE.findall(text)

def tokenize_sentences(text: str) -> List[str]:
    """Tokenize sentences / aphorisms."""
    if NLTK_AVAILABLE:
        try:
            import nltk
            raw_sents = nltk.sent_tokenize(text.strip())
        except Exception:
            raw_sents = SENTENCE_RE.split(text.strip())
    else:
        raw_sents = SENTENCE_RE.split(text.strip())
    return [s.strip() for s in raw_sents if len(s.strip()) > 3]

# ── Lemmatizer ────────────────────────────────────────────────────────────────
def lemmatize(word: str, pos: str = "NOUN") -> str:
    """Lemmatize a word using WordNet (if available) or fast rule-based fallback."""
    if NLTK_AVAILABLE:
        try:
            from nltk.stem import WordNetLemmatizer
            _wnl = WordNetLemmatizer()
            return _wnl.lemmatize(word.lower(), pos=_universal_to_wordnet(pos))
        except Exception:
            pass
    return simple_lemmatize(word)

def simple_lemmatize(word: str) -> str:
    """Fast rule-based lemmatizer (English). Used as fallback when NLTK is unavailable."""
    w = word.lower()
    if len(w) <= 3:
        return w
    # Past tense
    if w.endswith("ied") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith("eed") and len(w) > 4:
        return w[:-1]  # agreed → agree
    if w.endswith("ed") and len(w) > 4:
        if len(w) > 5 and w[-3] == w[-4] and w[-3] not in "aeiouy":
            return w[:-3]  # stopped → stop
        return w[:-2]
    # Gerund
    if w.endswith("ing") and len(w) > 5:
        if len(w) > 6 and w[-4] == w[-5] and w[-4] not in "aeiouy":
            return w[:-4]  # running → run
        stem = w[:-3]
        if stem and stem[-1] not in "aeiouy":
            return stem
        return w[:-3]
    # Plural
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith("ves") and len(w) > 4:
        if w in ("knives", "wives", "lives"):
            return w[:-3] + "fe"
        return w[:-3] + "f"
    if w.endswith("ses") or w.endswith("xes") or w.endswith("zes") or w.endswith("ches") or w.endswith("shes"):
        return w[:-2]
    if w.endswith("s") and not w.endswith("ss") and not w.endswith("us") and not w.endswith("is") and len(w) > 4:
        return w[:-1]
    return w

# ── POS Tagger ────────────────────────────────────────────────────────────────
def tag_pos_tokens(tokens: List[str]) -> List[Tuple[str, str]]:
    """
    Tag tokens with Universal POS tags: NOUN, VERB, ADJ, ADV, PRON, DET, ADP, CONJ, NUM, PRT, X
    Uses NLTK averaged_perceptron_tagger when available, heuristic fallback otherwise.
    """
    if NLTK_AVAILABLE:
        try:
            import nltk
            penn_tagged = nltk.pos_tag(tokens)
            return [(w, _ptb_to_universal(tag)) for w, tag in penn_tagged]
        except Exception as e:
            logger.debug(f"NLTK pos_tag failed ({e}), using heuristic tagger")
    return _heuristic_pos_tag(tokens)

def _heuristic_pos_tag(tokens: List[str]) -> List[Tuple[str, str]]:
    """Heuristic POS tagger (fallback only). Suffix-based contextual rules."""
    modal_verbs = {"can", "could", "will", "would", "shall", "should", "may", "might", "must"}
    aux_verbs = {"is", "am", "are", "was", "were", "be", "been", "being", "have", "has", "had",
                 "do", "does", "did", "doth", "hath"}
    pronouns = {"i", "me", "my", "myself", "we", "us", "our", "ours", "you", "your", "yours",
                "he", "him", "his", "she", "her", "hers", "it", "its", "they", "them", "their",
                "theirs", "thou", "thee", "thy", "thine", "ye", "who", "whom", "whose", "which",
                "what", "that", "this", "these", "those", "one", "someone", "everyone",
                "nothing", "everything"}
    determiners = {"a", "an", "the", "every", "each", "some", "any", "no", "all", "both",
                   "neither", "either"}
    prepositions = {"in", "on", "at", "to", "for", "with", "from", "by", "of", "about", "into",
                    "through", "during", "before", "after", "above", "below", "under", "between",
                    "among", "against", "upon", "without", "towards", "unto"}
    conjunctions = {"and", "but", "or", "nor", "for", "yet", "so", "because", "although",
                    "since", "unless", "while", "where", "whereas", "as"}
    adverbs = {"not", "never", "always", "often", "very", "too", "more", "most", "almost",
               "quite", "rather", "well", "even", "then", "now", "here", "there", "thus", "how",
               "why", "when", "again", "still", "already", "away", "back", "far"}

    tagged = []
    for i, token in enumerate(tokens):
        w = token.lower()
        if w in determiners:
            tagged.append((token, "DET"))
        elif w in pronouns:
            tagged.append((token, "PRON"))
        elif w in prepositions:
            tagged.append((token, "ADP"))
        elif w in conjunctions:
            tagged.append((token, "CONJ"))
        elif w in modal_verbs or w in aux_verbs:
            tagged.append((token, "VERB"))
        elif w in adverbs or w.endswith("ly"):
            tagged.append((token, "ADV"))
        elif (w.endswith("able") or w.endswith("ible") or w.endswith("al") or
              w.endswith("ful") or w.endswith("ic") or w.endswith("ive") or
              w.endswith("less") or w.endswith("ous") or w.endswith("ish")):
            tagged.append((token, "ADJ"))
        elif (w.endswith("tion") or w.endswith("sion") or w.endswith("ment") or
              w.endswith("ness") or w.endswith("ity") or w.endswith("ism") or
              w.endswith("ist") or w.endswith("dom") or w.endswith("ship")):
            tagged.append((token, "NOUN"))
        elif w.endswith("ed") or w.endswith("ing") or w.endswith("ize") or w.endswith("ise") or w.endswith("ate"):
            tagged.append((token, "VERB"))
        elif i > 0 and tagged[i - 1][1] in ("DET", "ADJ") and not w.endswith("ly"):
            tagged.append((token, "NOUN"))
        elif i > 0 and tagged[i - 1][1] == "PRON":
            tagged.append((token, "VERB"))
        else:
            tagged.append((token, "NOUN"))
    return tagged
