# Versioning

## How it works

Every time you run `[2] Sync repos` or `[9] Check for updates → merge`, NexusBrain records the exact commit SHA from each repo it merged. This is stored in `BRAIN/sync_state.json`.

```json
{
  "last_sync": "2026-05-01T12:00:00+00:00",
  "repos": {
    "my-core-brain": {
      "url": "https://github.com/user/my-core-brain",
      "branch": "main",
      "priority": 1,
      "synced_commit": "a3f8c1d9e2b4f6a8c0d2e4f6a8b0c2d4e6f8a0b2",
      "synced_at": "2026-05-01T12:00:00+00:00"
    },
    "community-brain": {
      "url": "https://github.com/org/community-brain",
      "branch": "main",
      "priority": 2,
      "synced_commit": "b9e2a4f1c3d5e7a9b1c3d5e7a9b1c3d5e7a9b1c3",
      "synced_at": "2026-04-28T09:15:00+00:00"
    }
  }
}
```

---

## Checking for updates

Menu option `[9] Check for updates` queries the GitHub Commits API for each repo's current HEAD commit and compares it with the recorded SHA.

```
=== Update Check ===

  Checking my-core-brain...   ✔ up to date     a3f8c1d
  Checking community-brain... ⬆ UPDATE         b9e2a4f → d1c7e3a
  Checking rust-brain...      ✖ never synced   → f2a1b3c

Merge 2 outdated repo(s)? (y/n):
```

- `✔ up to date` — recorded SHA matches current HEAD, no action needed
- `⬆ UPDATE` — new commits exist since last sync
- `✖ never synced` — repo is in `repo_list.json` but never synced

If you answer `y`, only the outdated and never-synced repos are merged. Repos that are up to date are skipped.

---

## No git required

NexusBrain uses only HTTP requests — no `git` binary needed:

- Category files: fetched via `https://raw.githubusercontent.com/owner/repo/branch/BRAIN/categories/*.json`
- HEAD SHA: fetched via `https://api.github.com/repos/owner/repo/commits/branch`

For private repositories, set `global_token` in `.nexusbrain`. See [configuration.md](configuration.md).

---

## GitHub API rate limits

Unauthenticated requests: 60 per hour per IP.
Authenticated (with `global_token`): 5,000 per hour.

If you have many repos or run updates frequently, set a token.
