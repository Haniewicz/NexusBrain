"""Add entries from incoming.json into BRAIN/categories/."""
import json
import sys
from pathlib import Path

CATEGORIES = ['languages', 'frameworks', 'patterns', 'integrations', 'pitfalls', 'architecture', 'tests']


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding='utf-8-sig'))
    except FileNotFoundError:
        print(f'❌ File not found: {path}')
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f'❌ Invalid JSON in {path}: {e}')
        sys.exit(1)


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def validate_incoming(incoming: dict, entry_schema: dict) -> None:
    try:
        from jsonschema import validate, ValidationError
    except ImportError:
        print('⚠ jsonschema not installed — skipping schema validation. Run: pip install jsonschema')
        return

    for category, entries in incoming.items():
        if category not in CATEGORIES:
            print(f'❌ Unknown category: "{category}"')
            sys.exit(1)
        if not isinstance(entries, dict):
            print(f'❌ Category "{category}" must be an object, got {type(entries).__name__}')
            sys.exit(1)
        try:
            validate(instance=entries, schema=entry_schema)
        except ValidationError as e:
            print(f'❌ Schema error in "{category}": {e.message}')
            sys.exit(1)


def merge_category(category: str, incoming_entries: dict, brain_dir: Path) -> list:
    """Merge incoming entries into the category file. Returns list of conflict keys."""
    cat_path = brain_dir / 'categories' / f'{category}.json'
    existing = load(cat_path) if cat_path.exists() else {}

    conflicts = []
    for key, value in incoming_entries.items():
        if key in existing:
            conflicts.append(key)
        else:
            existing[key] = value

    save(cat_path, existing)
    return conflicts


def update_manifest(brain_dir: Path) -> None:
    manifest_path = brain_dir / 'manifest.json'
    manifest = load(manifest_path) if manifest_path.exists() else {'v': 1, 'categories': {}}

    for category in CATEGORIES:
        cat_path = brain_dir / 'categories' / f'{category}.json'
        if cat_path.exists():
            data = load(cat_path)
            manifest['categories'][category] = sorted(data.keys())
        else:
            manifest['categories'][category] = []

    save(manifest_path, manifest)


def run(brain_dir: Path, input_path: Path) -> None:
    """Merge entries from input_path into brain_dir."""
    entry_schema_path = brain_dir / 'schema' / 'entry.schema.json'
    entry_schema = load(entry_schema_path) if entry_schema_path.exists() else {}

    incoming = load(input_path)
    validate_incoming(incoming, entry_schema)

    total_added = 0
    total_conflicts = 0

    for category, entries in incoming.items():
        conflicts = merge_category(category, entries, brain_dir)
        added = len(entries) - len(conflicts)
        total_added += added
        total_conflicts += len(conflicts)

        if conflicts:
            print(f'⚠ [{category}] {len(conflicts)} conflict(s) — kept existing: {", ".join(conflicts)}')
        if added:
            print(f'✔ [{category}] Added {added} entry/entries.')

    update_manifest(brain_dir)
    print(f'\n✔ Merge completed: {total_added} added, {total_conflicts} skipped (conflicts).')
