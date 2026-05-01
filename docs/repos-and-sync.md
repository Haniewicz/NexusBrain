# Repositories and Sync

## repo_list.json

Located at `BRAIN/repo_list.json`. Defines external repositories to pull knowledge from.

```json
{
  "repos": [
    {
      "name": "my-core-brain",
      "url": "https://github.com/username/my-core-brain",
      "branch": "main",
      "brain_path": "BRAIN",
      "priority": 1
    },
    {
      "name": "community-python-brain",
      "url": "https://github.com/org/python-brain",
      "branch": "main",
      "brain_path": "BRAIN",
      "priority": 2
    }
  ]
}
```

### Fields

| Field | Description |
|-------|-------------|
| `name` | Unique name for this repo (used in logs and status) |
| `url` | Full GitHub URL: `https://github.com/owner/repo` |
| `branch` | Branch to fetch from |
| `brain_path` | Path to the `BRAIN/` folder inside the repo |
| `priority` | Integer — **lower number = higher priority** |

---

## Priority system

When two repos contain an entry with the same key in the same category, priority determines which wins.

**Rule: lower priority number = higher priority.**

### Different priorities → automatic resolution

If `priority=1` and `priority=2` both have key `FastAPI` in `frameworks`, the `priority=1` entry wins automatically. The decision is logged to `BRAIN/sync_log.json` — no user input needed.

### Same priority → interactive resolution

If two repos share a priority and both have the same key, NexusBrain prompts you:

```
CONFLICT [frameworks > FastAPI]  (priority=1 vs priority=1)
[A] repo-community: "Async Python framework, use lifespan"
[B] repo-specialist: "FastAPI 0.100+: prefer annotated dependencies"
[S] Skip — do not merge this key
Choice (A/B/S):
```

See [conflicts.md](conflicts.md) for full details.

---

## Schema compatibility check

Before merging any repo, NexusBrain fetches its `entry.schema.json` and verifies it's compatible with your local schema. If incompatible, the repo is skipped with a warning.

This prevents malformed entries from polluting your brain.

Repos are considered compatible if their entry schema uses the same base type (`object`). Do not modify `BRAIN/schema/entry.schema.json` — keep it identical to the original to maintain compatibility with all community brain repos.

---

## Adding repos

**Via menu:**
```
python nexus.py
[7] Add repo
```

**Manually:** edit `BRAIN/repo_list.json` directly, then run `[2] Sync repos`.

---

## What sync does

1. Loads `repo_list.json` and sorts repos by priority (ascending)
2. For each repo: verifies schema, fetches HEAD SHA, downloads category files
3. Merges entries using priority rules (auto or interactive)
4. Writes updated category files and `manifest.json`
5. Saves commit SHA and timestamp to `sync_state.json`
6. Logs auto-resolved conflicts to `sync_log.json`
