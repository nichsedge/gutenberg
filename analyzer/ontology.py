import re
from typing import Dict, Any, List
from collections import Counter
from analyzer.nltk_helper import tokenize_words

# Curated Philosophical Ontology for Nietzsche & 19th Century Thought
PHILOSOPHICAL_ONTOLOGY = {
    "Will to Power": {
        "category": "Metaphysics / Psychology",
        "keywords": ["power", "will", "command", "ruling", "strength", "striving", "force", "mastery"],
        "description": "The fundamental driving force behind human behavior, nature, and reality."
    },
    "Übermensch (Overman)": {
        "category": "Ethics / Anthropology",
        "keywords": ["superman", "overman", "ubermensch", "higher man", "creator", "overcoming", "lightning"],
        "description": "The idealized higher being who creates new values and overcomes nihilism."
    },
    "Eternal Recurrence": {
        "category": "Cosmology / Existentialism",
        "keywords": ["eternal", "recurrence", "return", "circle", "eternity", "ring", "heaviest weight", "again"],
        "description": "The cosmic thought experiment: living the same life repeatedly for eternity."
    },
    "Master-Slave Morality": {
        "category": "Moral Philosophy",
        "keywords": ["master", "slave", "noble", "herd", "aristocratic", "ressentiment", "pity", "subjugation"],
        "description": "The dual typology of value systems: noble self-affirmation vs. reactive morality."
    },
    "Apollonian & Dionysian": {
        "category": "Aesthetics / Metaphysics",
        "keywords": ["apollo", "apollonian", "dionysus", "dionysian", "tragedy", "ecstasy", "illusion", "music", "intoxication"],
        "description": "The tension between rational, structured beauty (Apollo) and chaotic, primordial ecstasy (Dionysus)."
    },
    "Nihilism": {
        "category": "Existentialism / History",
        "keywords": ["nihilism", "nihilist", "void", "meaningless", "abyss", "ruin", "pessimism", "nothingness"],
        "description": "The condition where the highest values devaluate themselves; loss of ultimate meaning."
    },
    "God is Dead": {
        "category": "Theology / Culture",
        "keywords": ["god", "dead", "deity", "murder", "divine", "holy", "temple", "churches", "shadows"],
        "description": "The cultural collapse of Christian theistic foundations and transcendental authority."
    },
    "The Last Man": {
        "category": "Anthropology / Culture",
        "keywords": ["last man", "comfort", "small", "happiness", "pleasure", "blink", "contented", "mediocrity"],
        "description": "The antithesis of the Overman: seeking only comfort, safety, and petty equality."
    },
    "Amor Fati": {
        "category": "Existential Ethics",
        "keywords": ["fate", "destiny", "amor", "love of fate", "necessity", "affirmation", "inevitable"],
        "description": "Loving one's fate; embracing every joy and suffering without wishing anything different."
    },
    "Perspectivism": {
        "category": "Epistemology",
        "keywords": ["truth", "perspective", "interpretation", "knowledge", "illusion", "mask", "error", "appearances"],
        "description": "The epistemological view that there are no objective facts, only interpretations."
    },
    "Ressentiment": {
        "category": "Psychology",
        "keywords": ["revenge", "envy", "ressentiment", "spite", "resentment", "malice", "vengeance", "reactive"],
        "description": "Psychological state where frustrated weakness turns inward and invents moral condemnation."
    },
    "Asceticism": {
        "category": "Ascetic Ideals",
        "keywords": ["ascetic", "priest", "chastity", "fasting", "denial", "monk", "sin", "guilt", "penance"],
        "description": "The denial of earthly instincts in pursuit of spiritual purity or self-punishment."
    }
}

# Category Color Mapping
CATEGORY_COLORS = {
    "Metaphysics / Psychology": "#f59e0b",
    "Ethics / Anthropology": "#10b981",
    "Cosmology / Existentialism": "#8b5cf6",
    "Moral Philosophy": "#ef4444",
    "Aesthetics / Metaphysics": "#ec4899",
    "Existentialism / History": "#6b7280",
    "Theology / Culture": "#3b82f6",
    "Anthropology / Culture": "#14b8a6",
    "Existential Ethics": "#06b6d4",
    "Epistemology": "#eab308",
    "Psychology": "#f43f5e",
    "Ascetic Ideals": "#64748b"
}

def extract_ontology_data(book_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract ontology concepts, frequencies, matching passages, and co-occurrence network graph.
    """
    clean_text = book_data["clean_text"]
    words = tokenize_words(clean_text)
    verses = book_data.get("verses", [])
    
    # Calculate concept frequencies and matching verses
    concept_stats = []
    concept_verse_map = {}

    for concept_name, info in PHILOSOPHICAL_ONTOLOGY.items():
        kw_set = set(info["keywords"])
        matched_count = 0
        matching_verses = []

        # Check in words
        for w in words:
            if w in kw_set:
                matched_count += 1

        # Check in verses
        for v in verses:
            v_lower = v["text"].lower()
            if any(re.search(r'\b' + re.escape(kw) + r'\b', v_lower) for kw in kw_set):
                matching_verses.append(v)

        concept_stats.append({
            "name": concept_name,
            "category": info["category"],
            "description": info["description"],
            "frequency": matched_count,
            "verse_occurrences": len(matching_verses),
            "color": CATEGORY_COLORS.get(info["category"], "#6366f1"),
            "sample_passages": [
                {"chapter": v.get("chapter_title", "General"), "text": v["text"]}
                for v in matching_verses[:3]
            ]
        })
        concept_verse_map[concept_name] = {v["id"] for v in matching_verses}

    # Sort by frequency
    concept_stats.sort(key=lambda x: x["frequency"], reverse=True)

    # Build Co-occurrence Network Graph (Nodes & Edges)
    nodes = []
    edges = []
    
    for i, c in enumerate(concept_stats):
        nodes.append({
            "id": c["name"],
            "label": c["name"],
            "group": c["category"],
            "value": max(10, c["frequency"]),
            "title": f"<b>{c['name']}</b><br>Category: {c['category']}<br>Mentions: {c['frequency']}",
            "color": c["color"]
        })

    # Co-occurrence between concept pairs
    concept_names = [c["name"] for c in concept_stats]
    for i in range(len(concept_names)):
        c1 = concept_names[i]
        v_set1 = concept_verse_map[c1]
        for j in range(i + 1, len(concept_names)):
            c2 = concept_names[j]
            v_set2 = concept_verse_map[c2]
            overlap = len(v_set1.intersection(v_set2))
            if overlap > 0:
                edges.append({
                    "from": c1,
                    "to": c2,
                    "value": overlap,
                    "title": f"Co-occurs in {overlap} passages",
                    "width": max(1, min(8, overlap // 2 + 1))
                })

    return {
        "concepts_count": len(concept_stats),
        "concepts": concept_stats,
        "graph": {
            "nodes": nodes,
            "edges": edges
        }
    }
