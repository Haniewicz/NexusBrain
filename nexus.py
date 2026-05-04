#!/usr/bin/env python3
"""
NexusBrain — main entry point.

Interactive menu:  python nexus.py
CLI (used by AI):  python nexus.py query "<terms>"
                   python nexus.py add --category X --key K --value V
                   python nexus.py add-local --category X --key K --value V
"""
import argparse
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
BRAIN_DIR = BASE_DIR / 'BRAIN'

# Allow importing modules/ regardless of cwd
sys.path.insert(0, str(BASE_DIR))

CATEGORIES = ['languages', 'frameworks', 'patterns', 'integrations', 'pitfalls', 'architecture', 'tests']


# ── Config helpers ──────────────────────────────────────────────────────────

def _load_config() -> dict:
    config_path = Path.cwd() / '.nexusbrain'
    if config_path.exists():
        try:
            return json.loads(config_path.read_text(encoding='utf-8-sig'))
        except Exception:
            pass
    return {}


def _get_brain_dir(config: dict) -> Path:
    global_path = config.get('global_path')
    if global_path:
        p = Path(global_path) / 'BRAIN'
        if p.exists():
            return p
    return BRAIN_DIR


def _get_local_path(config: dict) -> Path | None:
    # Prefer project root derived from .nexusbrain location, fallback to cwd
    config_path = Path.cwd() / '.nexusbrain'
    project_root = config_path.parent if config_path.exists() else Path.cwd()
    local = project_root / 'BRAIN' / 'ai_memory.local.json'
    return local if local.exists() else None


def _get_token(config: dict) -> str | None:
    return config.get('global_token') or None


# ── Menu actions ─────────────────────────────────────────────────────────────

def _status(brain_dir: Path) -> None:
    try:
        data = json.loads((brain_dir / 'manifest.json').read_text(encoding='utf-8-sig'))
    except Exception:
        print('❌ Could not load manifest.json')
        return

    sync_state = {}
    ss_path = brain_dir / 'sync_state.json'
    if ss_path.exists():
        try:
            sync_state = json.loads(ss_path.read_text(encoding='utf-8-sig'))
        except Exception:
            pass

    print('\n=== NexusBrain Status ===\n')
    total = 0
    for cat, keys in data.get('categories', {}).items():
        count = len(keys)
        total += count
        print(f'  {cat:<15} {count:>4} entries')
    print(f'  {"─" * 21}')
    print(f'  {"TOTAL":<15} {total:>4}')
    last_sync = sync_state.get('last_sync') or 'never'
    repos_count = len(sync_state.get('repos', {}))
    print(f'\n  Last sync:    {last_sync}')
    print(f'  Synced repos: {repos_count}')


def _sync(brain_dir: Path, token: str | None) -> None:
    from modules.sync_repos import run
    run(brain_dir, token)


def _validate(brain_dir: Path, local_path: Path | None) -> None:
    from modules.validate import run
    ok = run(brain_dir, local_path)
    if not ok:
        sys.exit(1)


def _add_entries(brain_dir: Path) -> None:
    path_str = input('Path to incoming.json: ').strip().strip('"\'')
    input_path = Path(path_str)
    if not input_path.exists():
        print(f'❌ File not found: {input_path}')
        return
    from modules.merge import run
    run(brain_dir, input_path)


def _sync_log(brain_dir: Path) -> None:
    log_path = brain_dir / 'sync_log.json'
    if not log_path.exists():
        print('ℹ No sync log yet.')
        return
    try:
        data = json.loads(log_path.read_text(encoding='utf-8-sig'))
    except Exception:
        print('❌ Could not load sync_log.json')
        return

    entries = data.get('auto_resolved', [])
    if not entries:
        print('ℹ No auto-resolved conflicts recorded yet.')
        return

    print(f'\n=== Sync Log — last {min(20, len(entries))} of {len(entries)} auto-resolved ===\n')
    for e in entries[-20:]:
        print(f'  [{e.get("category")}/{e.get("key")}]')
        print(f'    Winner: {e.get("winner")} (priority={e.get("winner_priority")})')
        print(f'    Loser:  {e.get("loser")} (priority={e.get("loser_priority")})')
        print(f'    At:     {e.get("at", "?")}')
        print()


def _list_repos(brain_dir: Path) -> None:
    repo_list_path = brain_dir / 'repo_list.json'
    if not repo_list_path.exists():
        print('ℹ repo_list.json not found.')
        return
    try:
        data = json.loads(repo_list_path.read_text(encoding='utf-8-sig'))
    except Exception:
        print('❌ Could not load repo_list.json')
        return

    repos = data.get('repos', [])
    if not repos:
        print('ℹ No repos configured. Use [7] Add repo.')
        return

    sync_state = {}
    ss_path = brain_dir / 'sync_state.json'
    if ss_path.exists():
        try:
            sync_state = json.loads(ss_path.read_text(encoding='utf-8-sig')).get('repos', {})
        except Exception:
            pass

    print('\n=== Configured Repos ===\n')
    for r in sorted(repos, key=lambda x: x.get('priority', 99)):
        name = r.get('name', '?')
        state = sync_state.get(name, {})
        sha = state.get('synced_commit', '')
        sha_display = sha[:7] if sha else 'never synced'
        synced_at = (state.get('synced_at') or '—')[:10]
        print(f'  [p={r.get("priority", "?")}] {name}')
        print(f'         URL:    {r.get("url", "")}')
        print(f'         Branch: {r.get("branch", "main")}  Path: {r.get("brain_path", "BRAIN")}')
        print(f'         SHA:    {sha_display}  synced: {synced_at}')
        print()


def _add_repo(brain_dir: Path) -> None:
    print('\nAdd new repository:\n')
    name = input('  Name (e.g. community-python): ').strip()
    if not name:
        print('❌ Name cannot be empty.')
        return
    url = input('  URL (https://github.com/owner/repo): ').strip()
    branch = input('  Branch [main]: ').strip() or 'main'
    brain_path = input('  Brain path in repo [BRAIN]: ').strip() or 'BRAIN'
    priority_str = input('  Priority — lower = higher priority [10]: ').strip() or '10'

    try:
        priority = int(priority_str)
    except ValueError:
        print('❌ Priority must be an integer.')
        return

    repo_list_path = brain_dir / 'repo_list.json'
    if repo_list_path.exists():
        try:
            data = json.loads(repo_list_path.read_text(encoding='utf-8-sig'))
        except Exception:
            data = {'repos': []}
    else:
        data = {'repos': []}

    if any(r.get('name') == name for r in data.get('repos', [])):
        print(f'❌ Repo "{name}" already exists in repo_list.json.')
        return

    data.setdefault('repos', []).append({
        'name': name,
        'url': url,
        'branch': branch,
        'brain_path': brain_path,
        'priority': priority
    })
    repo_list_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'✔ Repo "{name}" added. Run [2] Sync repos to merge it.')


def _export(brain_dir: Path) -> None:
    print('\nAvailable categories: ' + ', '.join(CATEGORIES))
    selection = input('Export (comma-separated or "all"): ').strip()
    selected = CATEGORIES if selection.lower() == 'all' else [
        c.strip() for c in selection.split(',') if c.strip() in CATEGORIES
    ]
    if not selected:
        print('❌ No valid categories selected.')
        return

    output = {}
    for cat in selected:
        path = brain_dir / 'categories' / f'{cat}.json'
        if path.exists():
            try:
                output[cat] = json.loads(path.read_text(encoding='utf-8-sig'))
            except Exception:
                pass

    out_path = Path.cwd() / 'brain_export.json'
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
    total = sum(len(v) for v in output.values())
    print(f'✔ Exported {total} entries to {out_path}')


def _check_updates(brain_dir: Path, token: str | None) -> None:
    from modules.check_updates import run as check_run
    outdated = check_run(brain_dir, token)

    if not outdated:
        print('\n✔ All repos are up to date.')
        return

    choice = input(f'\nMerge {len(outdated)} outdated repo(s)? (y/n): ').strip().lower()
    if choice == 'y':
        from modules.sync_repos import run as sync_run
        sync_run(brain_dir, token, repos_override=outdated)


# ── CLI actions (called by AI) ────────────────────────────────────────────────

def _cli_query(brain_dir: Path, local_path: Path | None, query: str) -> None:
    from modules.query import run
    results = run(brain_dir, query, local_path)
    print(json.dumps(results, indent=2, ensure_ascii=False))


def _cli_add(brain_dir: Path, category: str, key: str, value: str, local: bool = False) -> None:
    if category not in CATEGORIES:
        print(f'❌ Unknown category: "{category}". Valid: {", ".join(CATEGORIES)}')
        sys.exit(1)
    if len(value) > 200:
        print('❌ Value exceeds 200 characters.')
        sys.exit(1)

    if local:
        config_path_root = Path.cwd() / '.nexusbrain'
        project_root = config_path_root.parent if config_path_root.exists() else Path.cwd()
        local_path = project_root / 'BRAIN' / 'ai_memory.local.json'
        if not local_path.exists():
            print(f'❌ Local brain not found at {local_path}')
            sys.exit(1)
        try:
            data = json.loads(local_path.read_text(encoding='utf-8-sig'))
        except Exception:
            data = {cat: {} for cat in CATEGORIES}

        data.setdefault(category, {})
        if key in data[category]:
            print(f'⚠ Key "{key}" already exists in local brain — skipped.')
        else:
            data[category][key] = value
            local_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
            print(f'✔ Added "{key}" to local brain [{category}].')
    else:
        from modules.merge import merge_category, update_manifest
        conflicts = merge_category(category, {key: value}, brain_dir)
        if conflicts:
            print(f'⚠ Key "{key}" already exists in global brain — skipped.')
        else:
            update_manifest(brain_dir)
            print(f'✔ Added "{key}" to global brain [{category}].')


# ── Menu loop ─────────────────────────────────────────────────────────────────

def _show_menu() -> str:
    print('\n' + '═' * 30)
    print('  NexusBrain')
    print('═' * 30)
    print('  [1] Status')
    print('  [2] Sync repos')
    print('  [3] Validate')
    print('  [4] Add entries')
    print('  [5] Show sync log')
    print('  [6] List repos')
    print('  [7] Add repo')
    print('  [8] Export')
    print('  [9] Check for updates')
    print('  [0] Exit')
    print('═' * 30)
    return input('  Choice: ').strip()


def main() -> None:
    config = _load_config()
    brain_dir = _get_brain_dir(config)
    local_path = _get_local_path(config)
    token = _get_token(config)

    # Parse CLI args first
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('command', nargs='?', default=None)
    parser.add_argument('query_str', nargs='?', default=None)
    parser.add_argument('--category', '-c', default=None)
    parser.add_argument('--key', '-k', default=None)
    parser.add_argument('--value', '-v', default=None)
    parser.add_argument('--local', action='store_true')
    args, _ = parser.parse_known_args()

    # CLI mode
    if args.command == 'query' and args.query_str:
        _cli_query(brain_dir, local_path, args.query_str)
        return

    if args.command in ('add', 'add-local') and args.category and args.key and args.value:
        _cli_add(
            brain_dir, args.category, args.key, args.value,
            local=(args.command == 'add-local' or args.local)
        )
        return

    # Interactive menu mode
    actions = {
        '1': lambda: _status(brain_dir),
        '2': lambda: _sync(brain_dir, token),
        '3': lambda: _validate(brain_dir, local_path),
        '4': lambda: _add_entries(brain_dir),
        '5': lambda: _sync_log(brain_dir),
        '6': lambda: _list_repos(brain_dir),
        '7': lambda: _add_repo(brain_dir),
        '8': lambda: _export(brain_dir),
        '9': lambda: _check_updates(brain_dir, token),
    }

    while True:
        choice = _show_menu()
        print()
        if choice == '0':
            print('Bye!')
            break
        elif choice in actions:
            actions[choice]()
        else:
            print('  Invalid choice.')


if __name__ == '__main__':
    main()
