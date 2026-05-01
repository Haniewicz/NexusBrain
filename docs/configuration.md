# Configuration

## .nexusbrain

Place `.nexusbrain` in the root of your project. This is the only file you need to configure.

```json
{
  "global_path": "C:/brains/NEXUSBRAIN_GLOBAL",
  "relevant_categories": ["frameworks", "patterns", "pitfalls"],
  "global_token": null
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `global_path` | string | ✅ | Absolute path to the `NEXUSBRAIN_GLOBAL/` folder |
| `relevant_categories` | array | ❌ | Hints for AI — which categories are relevant to this project |
| `global_token` | string\|null | ❌ | GitHub Personal Access Token for private brain repos |

---

## global_path

Must point to the `NEXUSBRAIN_GLOBAL/` folder — **not** the `BRAIN/` subfolder inside it.

```
✅ "global_path": "C:/brains/NEXUSBRAIN_GLOBAL"
✅ "global_path": "/home/user/brains/NEXUSBRAIN_GLOBAL"
❌ "global_path": "C:/brains/NEXUSBRAIN_GLOBAL/BRAIN"
```

When AI runs `python <global_path>/nexus.py query "..."`, it automatically resolves `BRAIN/` internally.

---

## relevant_categories

Tells AI which categories are most relevant for this project. AI uses this as a hint when deciding how to interpret query results.

Available categories:
- `languages` — language-level patterns and quirks
- `frameworks` — framework tips and gotchas
- `patterns` — architecture and design patterns
- `integrations` — third-party service integration tips
- `pitfalls` — common mistakes to avoid
- `architecture` — system design decisions
- `tests` — testing strategies

Example for a Python backend project:
```json
"relevant_categories": ["languages", "frameworks", "patterns", "pitfalls"]
```

---

## global_token

Required only if your `NEXUSBRAIN_GLOBAL` repo is private on GitHub. Set a Personal Access Token with `repo` read scope:

```json
{
  "global_token": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

**Security:** Never commit `.nexusbrain` with a token to a public repository. Add `.nexusbrain` to `.gitignore` if it contains a token.

The token is used for:
- Fetching category files when running `[2] Sync repos`
- Checking commit SHAs when running `[9] Check for updates`
