"""Validate all BRAIN/ files against schemas."""
import json
import sys
from pathlib import Path

try:
    from jsonschema import validate, ValidationError
except ImportError:
    print('❌ Missing dependency: pip install jsonschema')
    sys.exit(1)

CATEGORIES = ['languages', 'frameworks', 'patterns', 'integrations', 'pitfalls', 'architecture', 'tests']


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding='utf-8-sig'))
    except FileNotFoundError:
        print(f'❌ File not found: {path}')
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f'❌ Invalid JSON in {path}: {e}')
        sys.exit(1)


def validate_categories(brain_dir: Path, entry_schema: dict) -> bool:
    ok = True
    cat_dir = brain_dir / 'categories'
    for category in CATEGORIES:
        cat_path = cat_dir / f'{category}.json'
        if not cat_path.exists():
            print(f'❌ Missing: categories/{category}.json')
            ok = False
            continue

        data = load_json(cat_path)
        try:
            validate(instance=data, schema=entry_schema)
        except ValidationError as e:
            print(f'❌ Schema error in categories/{category}.json: {e.message}')
            ok = False
            continue

        keys = list(data.keys())
        if len(keys) != len(set(keys)):
            dupes = [k for k in set(keys) if keys.count(k) > 1]
            print(f'❌ Duplicates in categories/{category}.json: {", ".join(dupes)}')
            ok = False

    if ok:
        print(f'✔ All {len(CATEGORIES)} category files valid.')
    return ok


def validate_manifest(brain_dir: Path, manifest_schema: dict) -> bool:
    manifest_path = brain_dir / 'manifest.json'
    manifest = load_json(manifest_path)

    try:
        validate(instance=manifest, schema=manifest_schema)
    except ValidationError as e:
        print(f'❌ Schema error in manifest.json: {e.message}')
        return False

    ok = True
    cat_dir = brain_dir / 'categories'
    for category in CATEGORIES:
        cat_path = cat_dir / f'{category}.json'
        actual_keys = sorted(load_json(cat_path).keys()) if cat_path.exists() else []
        manifest_keys = sorted(manifest.get('categories', {}).get(category, []))
        if actual_keys != manifest_keys:
            print(f'❌ manifest.json out of sync for "{category}". Run nexus.py [4] or rebuild manifest.')
            ok = False

    if ok:
        print('✔ manifest.json valid.')
    return ok


def validate_local(brain_dir: Path, entry_schema: dict, local_path: Path) -> bool:
    if not local_path.exists():
        print(f'⚠ Local brain not found at: {local_path}')
        return True

    data = load_json(local_path)
    ok = True
    for category, entries in data.items():
        if category not in CATEGORIES:
            print(f'❌ Unknown category in local brain: "{category}"')
            ok = False
            continue
        if not isinstance(entries, dict):
            print(f'❌ local["{category}"] must be an object')
            ok = False
            continue
        try:
            validate(instance=entries, schema=entry_schema)
        except ValidationError as e:
            print(f'❌ Schema error in local["{category}"]: {e.message}')
            ok = False

    if ok:
        print('✔ ai_memory.local.json valid.')
    return ok


def run(brain_dir: Path, local_path: Path | None = None) -> bool:
    entry_schema = load_json(brain_dir / 'schema' / 'entry.schema.json')
    manifest_schema = load_json(brain_dir / 'schema' / 'manifest.schema.json')

    ok = True
    ok = validate_categories(brain_dir, entry_schema) and ok
    ok = validate_manifest(brain_dir, manifest_schema) and ok
    if local_path:
        ok = validate_local(brain_dir, entry_schema, local_path) and ok

    if ok:
        print('\n✔ Validation passed.')
    else:
        print('\n❌ Validation failed.')
    return ok
