"""Sync BRAIN from external repositories listed in repo_list.json."""
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

from .merge import save, load, update_manifest, CATEGORIES


def _fetch(url: str, token: str | None = None) -> bytes | None:
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'NexusBrain/1.0')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        print(f'  ⚠ HTTP {e.code} for {url}')
        return None
    except urllib.error.URLError as e:
        print(f'  ⚠ Network error: {e.reason}')
        return None


def _parse_github_url(url: str) -> tuple | None:
    """Parse 'https://github.com/owner/repo' → (owner, repo)."""
    url = url.rstrip('/')
    if url.startswith('https://github.com/'):
        parts = url[len('https://github.com/'):].split('/')
        if len(parts) >= 2:
            return parts[0], parts[1]
    return None


def get_head_sha(owner: str, repo: str, branch: str, token: str | None) -> str | None:
    api_url = f'https://api.github.com/repos/{owner}/{repo}/commits/{branch}'
    data = _fetch(api_url, token)
    if data is None:
        return None
    try:
        return json.loads(data)['sha']
    except (KeyError, json.JSONDecodeError):
        return None


def _fetch_remote_brain(owner: str, repo: str, branch: str, brain_path: str, token: str | None) -> dict:
    """Fetch all category files from a remote repo."""
    remote_data = {}
    for category in CATEGORIES:
        raw_url = f'https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{brain_path}/categories/{category}.json'
        data = _fetch(raw_url, token)
        if data is None:
            continue
        try:
            remote_data[category] = json.loads(data.decode('utf-8-sig'))
        except json.JSONDecodeError:
            print(f'  ⚠ Could not parse {category}.json from {owner}/{repo}')
    return remote_data


def _fetch_remote_schema(owner: str, repo: str, branch: str, brain_path: str, token: str | None) -> dict | None:
    raw_url = f'https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{brain_path}/schema/entry.schema.json'
    data = _fetch(raw_url, token)
    if data is None:
        return None
    try:
        return json.loads(data.decode('utf-8'))
    except json.JSONDecodeError:
        return None


def _schemas_compatible(local: dict, remote: dict) -> bool:
    return local.get('type') == remote.get('type')


def _merge_with_priority(
    remote_data: dict,
    repo_name: str,
    priority: int,
    existing: dict
) -> tuple:
    """
    Merge remote_data into existing priority map.
    existing: {category: {key: {'priority': int, 'value': any, 'source': str}}}
    Returns (updated_existing, auto_log, same_priority_conflicts).
    """
    auto_log = []
    same_priority_conflicts = []

    for category, entries in remote_data.items():
        if category not in CATEGORIES:
            continue
        existing.setdefault(category, {})

        for key, value in entries.items():
            if key not in existing[category]:
                existing[category][key] = {'priority': priority, 'value': value, 'source': repo_name}
            else:
                current = existing[category][key]
                if priority < current['priority']:
                    # New repo has higher priority (lower number) — auto-win
                    auto_log.append({
                        'category': category, 'key': key,
                        'winner': repo_name, 'winner_priority': priority,
                        'loser': current['source'], 'loser_priority': current['priority'],
                        'kept_value': value
                    })
                    existing[category][key] = {'priority': priority, 'value': value, 'source': repo_name}
                elif priority > current['priority']:
                    # Existing has higher priority — skip, log
                    auto_log.append({
                        'category': category, 'key': key,
                        'winner': current['source'], 'winner_priority': current['priority'],
                        'loser': repo_name, 'loser_priority': priority,
                        'kept_value': current['value']
                    })
                else:
                    # Same priority — needs interactive resolution
                    same_priority_conflicts.append({
                        'category': category, 'key': key,
                        'a_repo': current['source'], 'a_value': current['value'],
                        'b_repo': repo_name, 'b_value': value,
                        'ref': existing[category][key]
                    })

    return existing, auto_log, same_priority_conflicts


def _resolve_interactive(conflicts: list) -> None:
    """Interactive prompt for same-priority conflicts."""
    if not conflicts:
        return

    print(f'\n⚡ {len(conflicts)} same-priority conflict(s) need your input:\n')
    for c in conflicts:
        val_a = c['a_value'] if isinstance(c['a_value'], str) else json.dumps(c['a_value'])
        val_b = c['b_value'] if isinstance(c['b_value'], str) else json.dumps(c['b_value'])

        print(f'  CONFLICT [{c["category"]} > {c["key"]}]')
        print(f'  [A] {c["a_repo"]}: {val_a[:120]}')
        print(f'  [B] {c["b_repo"]}: {val_b[:120]}')
        print(f'  [S] Skip — do not merge this key')

        while True:
            choice = input('  Choice (A/B/S): ').strip().upper()
            if choice == 'A':
                break  # Keep existing (already in place)
            elif choice == 'B':
                c['ref']['value'] = c['b_value']
                c['ref']['source'] = c['b_repo']
                break
            elif choice == 'S':
                c['ref']['_skip'] = True
                break
            else:
                print('  Please enter A, B, or S.')
        print()


def _apply_to_categories(brain_dir: Path, merged: dict) -> None:
    """Write merged priority map into actual category JSON files."""
    for category in CATEGORIES:
        cat_path = brain_dir / 'categories' / f'{category}.json'
        existing = {}
        if cat_path.exists():
            try:
                existing = json.loads(cat_path.read_text(encoding='utf-8-sig'))
            except Exception:
                pass

        for key, info in merged.get(category, {}).items():
            if info.get('_skip'):
                continue
            existing[key] = info['value']

        save(cat_path, existing)

    update_manifest(brain_dir)


def run(brain_dir: Path, token: str | None = None, repos_override: list | None = None) -> None:
    """Sync brain from external repositories."""
    if repos_override is not None:
        repos = repos_override
    else:
        repo_list = load(brain_dir / 'repo_list.json')
        repos = repo_list.get('repos', [])

    if not repos:
        print('ℹ No repos configured in repo_list.json.')
        return

    local_schema = {}
    local_schema_path = brain_dir / 'schema' / 'entry.schema.json'
    if local_schema_path.exists():
        local_schema = load(local_schema_path)

    sync_state_path = brain_dir / 'sync_state.json'
    sync_state = load(sync_state_path) if sync_state_path.exists() else {'last_sync': None, 'repos': {}}

    sync_log_path = brain_dir / 'sync_log.json'
    sync_log = load(sync_log_path) if sync_log_path.exists() else {'auto_resolved': []}

    repos_sorted = sorted(repos, key=lambda r: r.get('priority', 99))

    # Priority-aware merge accumulator
    existing_priorities: dict = {}
    all_auto_logs = []
    all_same_priority_conflicts = []

    for repo_cfg in repos_sorted:
        name = repo_cfg.get('name', 'unknown')
        url = repo_cfg.get('url', '')
        branch = repo_cfg.get('branch', 'main')
        brain_path = repo_cfg.get('brain_path', 'BRAIN')
        priority = repo_cfg.get('priority', 99)

        parsed = _parse_github_url(url)
        if not parsed:
            print(f'⚠ Cannot parse GitHub URL for "{name}": {url}')
            continue

        owner, repo = parsed
        print(f'\n🔄 Syncing "{name}" (priority={priority})...')

        remote_schema = _fetch_remote_schema(owner, repo, branch, brain_path, token)
        if remote_schema and local_schema and not _schemas_compatible(local_schema, remote_schema):
            print(f'  ⚠ Schema incompatible — skipping "{name}".')
            continue

        sha = get_head_sha(owner, repo, branch, token)
        if sha is None:
            print(f'  ⚠ Could not fetch commit SHA — skipping "{name}".')
            continue

        remote_data = _fetch_remote_brain(owner, repo, branch, brain_path, token)
        if not remote_data:
            print(f'  ⚠ No data fetched from "{name}".')
            continue

        existing_priorities, auto_log, same_conflicts = _merge_with_priority(
            remote_data, name, priority, existing_priorities
        )
        all_auto_logs.extend(auto_log)
        all_same_priority_conflicts.extend(same_conflicts)

        sync_state['repos'][name] = {
            'url': url,
            'branch': branch,
            'priority': priority,
            'synced_commit': sha,
            'synced_at': datetime.now(timezone.utc).isoformat()
        }

        count = sum(len(v) for v in remote_data.values())
        print(f'  ✔ Fetched {count} entries.')

    _resolve_interactive(all_same_priority_conflicts)
    _apply_to_categories(brain_dir, existing_priorities)

    sync_state['last_sync'] = datetime.now(timezone.utc).isoformat()
    save(sync_state_path, sync_state)

    if all_auto_logs:
        ts = datetime.now(timezone.utc).isoformat()
        sync_log.setdefault('auto_resolved', []).extend(
            [{**entry, 'at': ts} for entry in all_auto_logs]
        )
        save(sync_log_path, sync_log)

    print(f'\n✔ Sync completed. Auto-resolved: {len(all_auto_logs)}, Interactive: {len(all_same_priority_conflicts)}.')
