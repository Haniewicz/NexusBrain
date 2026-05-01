# Contributing — Share Your Brain

You can share your brain entries with the community in two ways:
1. Submit a Pull Request to the main NexusBrain repo
2. Publish your own compatible brain repo for others to sync from

---

## Option 1: Pull Request to the main repo

### Step 1 — Fork the repository

Fork `NEXUSBRAIN_GLOBAL` on GitHub.

### Step 2 — Clone your fork and add entries

```
git clone https://github.com/YOUR_USERNAME/NEXUSBRAIN_GLOBAL
cd NEXUSBRAIN_GLOBAL
```

Add entries using the menu or by creating `incoming.json` and running `[4] Add entries`:

```json
{
  "frameworks": {
    "FastAPI-lifespan": "Use lifespan context manager instead of on_event (deprecated since 0.93)."
  },
  "pitfalls": {
    "mutable-default-arg": "Never use mutable default args in Python — value is shared across all calls."
  }
}
```

```
python nexus.py
[4] Add entries
Path to incoming.json: incoming.json
```

### Step 3 — Validate

```
python nexus.py
[3] Validate
```

Must pass with no errors before submitting.

### Step 4 — Check schema compatibility

**Do NOT modify** `BRAIN/schema/entry.schema.json`. The schema must be identical to the original. Any changes break compatibility with all other brain repos.

### Step 5 — Commit changed files

Only commit files from `BRAIN/categories/` and `BRAIN/manifest.json`. Do not commit `sync_state.json`, `sync_log.json`, or any personal config.

```
git add BRAIN/categories/ BRAIN/manifest.json
git commit -m "Add FastAPI lifespan and mutable default arg pitfall"
git push
```

### Step 6 — Open a Pull Request

Your PR description should include:
- Which categories you're adding to
- Source of the knowledge (official docs, personal experience, known best practices)
- Confirmation that `[3] Validate` passes
- Confirmation that entries are generic, not project-specific

### What gets accepted

✅ Generic best practices applicable across many projects
✅ Common pitfalls with clear, actionable descriptions
✅ Tips for widely-used frameworks or libraries
✅ Entries that fit in 200 characters

❌ Project-specific decisions or internal details
❌ Entries exceeding 200 characters
❌ Opinionated preferences without clear justification
❌ Modified `schema/entry.schema.json`

---

## Option 2: Publish your own brain repo

Create your own compatible brain repo that anyone can add to their `repo_list.json`.

### Requirements for compatibility

1. Must have a `BRAIN/` folder (or custom path matching `brain_path`)
2. Must have `BRAIN/schema/entry.schema.json` with the same base `"type": "object"` structure
3. Must have `BRAIN/categories/` with valid JSON files following the entry schema
4. Must have `BRAIN/manifest.json` in sync with the category files

### How others add your repo

They add an entry to their `BRAIN/repo_list.json`:

```json
{
  "repos": [
    {
      "name": "your-brain",
      "url": "https://github.com/you/your-brain-repo",
      "branch": "main",
      "brain_path": "BRAIN",
      "priority": 5
    }
  ]
}
```

Then run `[2] Sync repos`.

### Maintaining your brain repo

- Keep `BRAIN/manifest.json` in sync with categories (run `[3] Validate` to check)
- Use consistent entry format (prefer plain strings ≤ 200 chars)
- Use tags in structured entries to improve search relevance
- Document the scope of your brain in your repo's README (e.g., "Python + FastAPI focused")
