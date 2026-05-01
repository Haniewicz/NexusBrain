"""Check external repositories for available updates."""
import json
import urllib.request
import urllib.error
from pathlib import Path

from .merge import load, CATEGORIES


def _fetch(url: str, token: str | None = None) -> bytes | None:
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'NexusBrain/1.0')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        print(f'⚠ HTTP {e.code}')
        return None
    except urllib.error.URLError as e:
        print(f'⚠ Network error: {e.reason}')
        return None


def _get_head_sha(url: str, branch: str, token: str | None) -> str | None:
    url = url.rstrip('/')
    if not url.startswith('https://github.com/'):
        return None
    parts = url[len('https://github.com/'):].split('/')
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1]
    api_url = f'https://api.github.com/repos/{owner}/{repo}/commits/{branch}'
    data = _fetch(api_url, token)
    if data:
        try:
            return json.loads(data)['sha']
        except (KeyError, json.JSONDecodeError):
            pass
    return None


def run(brain_dir: Path, token: str | None = None) -> list:
    """Check all repos for updates. Returns list of outdated repo configs."""
    repo_list = load(brain_dir / 'repo_list.json')
    repos = repo_list.get('repos', [])

    if not repos:
        print('ℹ No repos configured in repo_list.json.')
        return []

    sync_state_path = brain_dir / 'sync_state.json'
    synced = load(sync_state_path).get('repos', {}) if sync_state_path.exists() else {}

    print('\n=== Update Check ===\n')

    outdated = []
    for repo_cfg in repos:
        name = repo_cfg.get('name', 'unknown')
        url = repo_cfg.get('url', '')
        branch = repo_cfg.get('branch', 'main')
        state = synced.get(name, {})
        synced_sha = state.get('synced_commit')

        print(f'  Checking {name}...', end=' ', flush=True)
        current_sha = _get_head_sha(url, branch, token)

        if current_sha is None:
            print('⚠ Could not fetch')
            continue

        short_current = current_sha[:7]

        if synced_sha is None:
            print(f'✖ never synced   → {short_current}')
            outdated.append(repo_cfg)
        elif synced_sha == current_sha:
            print(f'✔ up to date     {short_current}')
        else:
            print(f'⬆ UPDATE         {synced_sha[:7]} → {short_current}')
            outdated.append(repo_cfg)

    return outdated
