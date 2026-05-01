# AI Protocol

NexusBrain is designed to be **fully automatic** — you write a prompt, the AI queries the brain and uses the result. No manual steps required.

---

## Full flow

```
You write a prompt
      ↓
AI reads .github/copilot-instructions.md  (always loaded by VS Code Copilot)
      ↓
AI runs: python <global_path>/nexus.py query "<key terms>"
      ↓
Script does keyword + tag + fuzzy matching across global brain + local brain
Returns only the top matching entries as JSON (typically 3-10 entries, ~150 tokens)
      ↓
AI uses results as context and answers your question
      ↓
If AI created something reusable:
  → python <global_path>/nexus.py add --category <cat> --key "<k>" --value "<v>"

If AI created something project-specific:
  → python <global_path>/nexus.py add-local --category <cat> --key "<k>" --value "<v>"
```

---

## How query works

The `query` command scores every entry by relevance to the search terms:

| Match type | Score |
|------------|-------|
| Term found in entry key | +3 |
| Term found in entry value/tip | +2 |
| Term found in tags | +4 |

Returns top 10 matches as JSON. Local brain entries override global entries with the same key.

Example:
```
python nexus.py query "Redis FastAPI connection"
```
Returns:
```json
{
  "integrations": {
    "Redis-asyncio": "Use redis.asyncio for async FastAPI; never share connection across workers."
  },
  "pitfalls": {
    "redis-pool-shutdown": "Always close Redis pool on app shutdown via lifespan context manager."
  }
}
```

Returns `{}` if nothing matches — AI then generates a solution from scratch.

---

## Decision: global vs local

| Scenario | Command | Example |
|----------|---------|---------|
| Generic best practice | `nexus.py add` | "Use lifespan in FastAPI for startup/shutdown" |
| Common pitfall | `nexus.py add` | "Never use mutable default args in Python" |
| Project-specific rule | `nexus.py add-local` | "Auth tokens expire in 1h in this project" |
| Internal config detail | `nexus.py add-local` | "Our Redis runs on redis://internal:6379/2" |

When in doubt: if the knowledge would be useful in **any** project using the same technology, it belongs in the global brain.

---

## Token efficiency

| Approach | Tokens loaded |
|----------|---------------|
| Full brain (old approach) | ~25,000 |
| Selective category files | ~5,000 |
| **NexusBrain query** | **~150** |

The query result replaces the need to load any category files directly.
