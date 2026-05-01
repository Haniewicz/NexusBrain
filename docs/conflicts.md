# Conflict Resolution

A conflict occurs when two repos contain an entry with the same key in the same category.

---

## Automatic resolution (different priorities)

If the conflicting repos have different priorities, the one with the **lower priority number** wins automatically. No user input needed.

**Example:** `priority=1` beats `priority=2` for key `FastAPI` in `frameworks`.

The decision is logged to `BRAIN/sync_log.json`:
```json
{
  "auto_resolved": [
    {
      "category": "frameworks",
      "key": "FastAPI",
      "winner": "my-core-brain",
      "winner_priority": 1,
      "loser": "community-brain",
      "loser_priority": 2,
      "kept_value": "Async framework; use lifespan for startup/shutdown.",
      "at": "2026-05-01T12:00:00+00:00"
    }
  ]
}
```

View auto-resolved conflicts via menu `[5] Show sync log`.

---

## Interactive resolution (same priority)

If two repos have the **same priority** and both have the same key, you are prompted to choose:

```
⚡ 2 same-priority conflict(s) need your input:

  CONFLICT [frameworks > FastAPI]
  [A] repo-community: "Async Python framework, use lifespan"
  [B] repo-specialist: "FastAPI 0.100+: prefer annotated deps"
  [S] Skip — do not merge this key
  Choice (A/B/S): 
```

Options:
- **A** — keep the value from the first repo (the one currently in the brain)
- **B** — use the value from the incoming repo
- **S** — skip this key entirely (neither value is merged)

---

## Avoiding conflicts

Use specific, descriptive key names. Instead of `FastAPI`, use:
- `FastAPI-lifespan`
- `FastAPI-dependencies`
- `FastAPI-exception-handlers`

Specific keys rarely conflict even across many repos.

Set clear priorities in `repo_list.json` so most conflicts resolve automatically:
- Your own curated brain: `priority=1`
- Trusted community brain: `priority=2`
- Specialized brain (e.g., Rust): `priority=3`
