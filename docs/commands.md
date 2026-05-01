# Commands Reference

## Running nexus.py

From the `NEXUSBRAIN_GLOBAL/` directory:
```
python nexus.py
```

From a project directory (reads `.nexusbrain` for config):
```
python C:/brains/NEXUSBRAIN_GLOBAL/nexus.py
```

---

## Interactive Menu

### [1] Status

Shows number of entries per category, total entry count, last sync time, and number of synced repos.

```
=== NexusBrain Status ===

  languages          2 entries
  frameworks         8 entries
  patterns           5 entries
  integrations       3 entries
  pitfalls          12 entries
  architecture       1 entries
  tests              0 entries
  ─────────────────────────
  TOTAL             31

  Last sync:    2026-05-01T12:00:00+00:00
  Synced repos: 2
```

### [2] Sync repos

Fetches all repositories from `BRAIN/repo_list.json` and merges their entries into your brain.

- Verifies schema compatibility before merging each repo
- Resolves conflicts by priority (see [conflicts.md](conflicts.md))
- Interactive prompt for same-priority conflicts
- Saves commit SHA per repo to `BRAIN/sync_state.json`
- Logs auto-resolved conflicts to `BRAIN/sync_log.json`

### [3] Validate

Validates all BRAIN/ files:
- All 7 category files against `BRAIN/schema/entry.schema.json`
- `BRAIN/manifest.json` against schema and actual category contents
- `BRAIN/ai_memory.local.json` if found in current directory (project usage)

Exits with error code 1 if any check fails.

### [4] Add entries

Prompts for path to an `incoming.json` file, validates it, and merges entries into the brain.

Format of `incoming.json`:
```json
{
  "frameworks": {
    "FastAPI-lifespan": "Use lifespan context manager instead of on_event (deprecated since 0.93)."
  },
  "pitfalls": {
    "mutable-default-arg": "Never use mutable default args — shared across all calls."
  }
}
```

Existing keys are never overwritten (conflict = skip with warning).

### [5] Show sync log

Displays the last 20 auto-resolved conflicts from `BRAIN/sync_log.json`. Shows which repo won, which lost, and when.

### [6] List repos

Shows all repos from `BRAIN/repo_list.json` with priority, last synced commit SHA, and sync date.

### [7] Add repo

Interactive prompt to add a new repository to `BRAIN/repo_list.json`:

```
Name (e.g. community-python): my-brain
URL (https://github.com/owner/repo): https://github.com/user/my-brain
Branch [main]: main
Brain path in repo [BRAIN]: BRAIN
Priority — lower = higher priority [10]: 2
```

After adding, run `[2] Sync repos`.

### [8] Export

Exports selected categories to a single `brain_export.json` file in the current directory. Useful for backup or sharing a snapshot.

```
Available categories: languages, frameworks, patterns, ...
Export (comma-separated or "all"): frameworks, patterns
✔ Exported 13 entries to brain_export.json
```

### [9] Check for updates

Queries the GitHub API for the current HEAD commit SHA of each synced repo. Compares with recorded SHA in `BRAIN/sync_state.json`.

```
=== Update Check ===

  Checking my-core-brain...  ✔ up to date     a3f8c1d
  Checking community-brain... ⬆ UPDATE         b9e2a4f → d1c7e3a
  Checking rust-brain...     ✖ never synced   → f2a1b3c

Merge 2 outdated repo(s)? (y/n):
```

If you choose `y`, only outdated repos are synced.

---

## CLI Mode (used by AI)

### query

```
python nexus.py query "<search terms>"
```

Searches global + local brain and returns matching entries as JSON. Used by AI before answering technical questions.

**Example:**
```
python nexus.py query "Redis FastAPI async"
```

**Output:**
```json
{
  "integrations": {
    "Redis-asyncio": "Use redis.asyncio for async FastAPI; close pool in lifespan."
  }
}
```

Returns `{}` if nothing matches.

### add

```
python nexus.py add --category <category> --key "<name>" --value "<description>"
```

Adds a single entry to the **global** brain. Used by AI for reusable knowledge.

- `--category` / `-c`: one of the 7 categories
- `--key` / `-k`: unique entry name (use kebab-case)
- `--value` / `-v`: description, max 200 characters

**Example:**
```
python nexus.py add --category pitfalls --key "N+1-query" --value "Use select_related/prefetch_related in Django to avoid N+1 DB queries."
```

### add-local

```
python nexus.py add-local --category <category> --key "<name>" --value "<description>"
```

Same as `add` but writes to `BRAIN/ai_memory.local.json` in the current working directory. Used by AI for project-specific knowledge.

Must be run from the project directory containing `BRAIN/ai_memory.local.json`.
