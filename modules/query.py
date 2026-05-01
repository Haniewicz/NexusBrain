"""Search the brain for matching entries. Used by AI via CLI."""
import json
from pathlib import Path

CATEGORIES = ['languages', 'frameworks', 'patterns', 'integrations', 'pitfalls', 'architecture', 'tests']


def _load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding='utf-8-sig'))
    except Exception:
        return {}


def _score(key: str, value, query_terms: list) -> int:
    """Return relevance score. Higher = more relevant."""
    score = 0
    key_lower = key.lower()

    if isinstance(value, str):
        value_lower = value.lower()
        tags = []
    else:
        value_lower = value.get('tip', '').lower()
        tags = [t.lower() for t in value.get('tags', [])]

    for term in query_terms:
        if term in key_lower:
            score += 3
        if term in value_lower:
            score += 2
        if any(term in tag for tag in tags):
            score += 4

    return score


def run(brain_dir: Path, query: str, local_path: Path | None = None, top_n: int = 10) -> dict:
    """Search global + local brain. Returns dict of top matching entries."""
    query_terms = [t.lower() for t in query.split() if len(t) > 1]

    # Collect scored candidates: {category: {key: {value, score, source}}}
    candidates: dict = {cat: {} for cat in CATEGORIES}

    # Global brain
    for category in CATEGORIES:
        cat_path = brain_dir / 'categories' / f'{category}.json'
        data = _load(cat_path)
        for key, value in data.items():
            s = _score(key, value, query_terms)
            if s > 0:
                candidates[category][key] = {'value': value, 'score': s, 'source': 'global'}

    # Local brain — overrides global entries with same key
    if local_path and local_path.exists():
        local_data = _load(local_path)
        for category, entries in local_data.items():
            if category not in CATEGORIES:
                continue
            for key, value in entries.items():
                s = _score(key, value, query_terms)
                if s > 0:
                    candidates[category][key] = {'value': value, 'score': s, 'source': 'local'}
                elif key in candidates.get(category, {}):
                    # Local override even if not a query match — replace global value
                    existing_score = candidates[category][key]['score']
                    candidates[category][key] = {'value': value, 'score': existing_score, 'source': 'local'}

    # Flatten, sort by score, keep top_n
    flat = [
        (category, key, info)
        for category, entries in candidates.items()
        for key, info in entries.items()
    ]
    flat.sort(key=lambda x: x[2]['score'], reverse=True)
    flat = flat[:top_n]

    # Rebuild output as clean {category: {key: value}}
    output: dict = {}
    for category, key, info in flat:
        output.setdefault(category, {})[key] = info['value']

    return output
