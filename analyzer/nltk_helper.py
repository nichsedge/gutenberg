import re
import string
from typing import List, Tuple, Set

# Universal POS tag set mapping & standard English stopwords
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
    "weren", "won", "wouldn", "thou", "thee", "thy", "thine", "ye", "unto", "doth", "hath", "art"
}

# Regex tokenizers for high speed and independence from external data downloads
WORD_RE = re.compile(r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b")
SENTENCE_RE = re.compile(r'(?<=[.!?])\s+(?=[A-Z"“\'\d])')

def tokenize_words(text: str, lower: bool = True) -> List[str]:
    """Tokenize words accurately."""
    if lower:
        return [w.lower() for w in WORD_RE.findall(text)]
    return WORD_RE.findall(text)

def tokenize_sentences(text: str) -> List[str]:
    """Tokenize sentences / aphorisms."""
    raw_sents = SENTENCE_RE.split(text.strip())
    results = []
    for s in raw_sents:
        clean = s.strip()
        if len(clean) > 3:
            results.append(clean)
    return results

def simple_lemmatize(word: str) -> str:
    """Fast rule-based lemmatizer for English."""
    w = word.lower()
    if len(w) > 4:
        if w.endswith("ies") and len(w) > 4:
            return w[:-3] + "y"
        if w.endswith("es") and (w.endswith("shes") or w.endswith("ches") or w.endswith("xes") or w.endswith("sses")):
            return w[:-2]
        if w.endswith("s") and not w.endswith("ss") and not w.endswith("us") and not w.endswith("is"):
            return w[:-1]
        if w.endswith("ing") and len(w) > 5:
            if w[-4] == w[-5] and w[-4] not in "aeiouy": # e.g. running -> run
                return w[:-4]
            return w[:-3]
        if w.endswith("ed") and len(w) > 4:
            if w.endswith("ied"):
                return w[:-3] + "y"
            return w[:-2] if w.endswith("eed") else w[:-2]
    return w

def tag_pos_tokens(tokens: List[str]) -> List[Tuple[str, str]]:
    """
    Tag tokens with Universal POS tags:
    NOUN, VERB, ADJ, ADV, PRON, DET, ADP (Preposition), CONJ, NUM, PRT (Particle), . (Punctuation), X
    Uses fast contextual heuristic tagger.
    """
    tagged = []
    modal_verbs = {"can", "could", "will", "would", "shall", "should", "may", "might", "must"}
    aux_verbs = {"is", "am", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "doth", "hath"}
    pronouns = {"i", "me", "my", "myself", "we", "us", "our", "ours", "you", "your", "yours", "he", "him", "his", "she", "her", "hers", "it", "its", "they", "them", "their", "theirs", "thou", "thee", "thy", "thine", "ye", "who", "whom", "whose", "which", "what", "that", "this", "these", "those", "one", "someone", "everyone", "nothing", "everything"}
    determiners = {"a", "an", "the", "every", "each", "some", "any", "no", "all", "both", "neither", "either"}
    prepositions = {"in", "on", "at", "to", "for", "with", "from", "by", "of", "about", "into", "through", "during", "before", "after", "above", "below", "under", "between", "among", "against", "upon", "without", "towards", "unto"}
    conjunctions = {"and", "but", "or", "nor", "for", "yet", "so", "because", "although", "since", "unless", "while", "where", "whereas", "as"}
    adverbs = {"not", "never", "always", "often", "very", "too", "more", "most", "almost", "quite", "rather", "well", "even", "then", "now", "here", "there", "thus", "how", "why", "when", "again", "still", "already", "away", "back", "far"}

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
        elif w.endswith("able") or w.endswith("ible") or w.endswith("al") or w.endswith("ful") or w.endswith("ic") or w.endswith("ive") or w.endswith("less") or w.endswith("ous") or w.endswith("ish"):
            tagged.append((token, "ADJ"))
        elif w.endswith("tion") or w.endswith("sion") or w.endswith("ment") or w.endswith("ness") or w.endswith("ity") or w.endswith("ism") or w.endswith("ist") or w.endswith("dom") or w.endswith("ship"):
            tagged.append((token, "NOUN"))
        elif w.endswith("ed") or w.endswith("ing") or w.endswith("ize") or w.endswith("ise") or w.endswith("ate"):
            tagged.append((token, "VERB"))
        elif i > 0 and tagged[i-1][1] in ("DET", "ADJ") and not w.endswith("ly"):
            tagged.append((token, "NOUN"))
        elif i > 0 and tagged[i-1][1] == "PRON":
            tagged.append((token, "VERB"))
        else:
            tagged.append((token, "NOUN"))
            
    return tagged
