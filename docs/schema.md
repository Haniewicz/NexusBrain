# Entry Format (Schema)

## Overview

Each category file is a JSON object where:
- **Key** — short unique identifier for the entry (kebab-case recommended)
- **Value** — short string (max 200 chars) or structured object with tags

---

## Formats

### String (preferred — minimal tokens)

```json
{
  "FastAPI-lifespan": "Use lifespan context manager instead of on_event (deprecated since 0.93).",
  "redis-pool-shutdown": "Always close Redis connection pool on app shutdown to prevent connection leaks."
}
```

### Structured object (when tags improve search)

```json
{
  "FastAPI-lifespan": {
    "tip": "Use lifespan context manager instead of on_event (deprecated since 0.93).",
    "tags": ["fastapi", "startup", "shutdown", "async", "lifespan"]
  }
}
```

Tags (max 5 items) significantly improve search relevance. Use technology names, concepts, and synonyms that someone might type when searching for this entry.

---

## Categories

| Category | What belongs here |
|----------|------------------|
| `languages` | Language-level patterns, quirks, type system tips |
| `frameworks` | Framework-specific best practices and gotchas |
| `patterns` | Architecture and design patterns |
| `integrations` | Third-party service integration guides |
| `pitfalls` | Common mistakes with actionable fixes |
| `architecture` | System design decisions and structural rules |
| `tests` | Testing strategies, examples, and anti-patterns |

---

## Good vs bad entries

✅ Specific and actionable:
```json
"redis-pool-shutdown": "Always close Redis connection pool on shutdown to prevent leaks."
```

✅ Uses tags for discoverability:
```json
"FastAPI-lifespan": {
  "tip": "Use lifespan context manager, not on_event (deprecated since 0.93).",
  "tags": ["fastapi", "startup", "shutdown", "lifespan"]
}
```

❌ Too vague:
```json
"redis": "Use Redis carefully."
```

❌ Too long (over 200 characters):
```json
"redis-pool": "When using Redis with FastAPI, make sure to properly configure the connection pool settings and close it during application shutdown events using the lifespan context manager or startup/shutdown event handlers..."
```

❌ Project-specific (use local brain instead):
```json
"our-redis-url": "redis://internal-redis.prod:6379/2"
```

---

## Schema file

Located at `BRAIN/schema/entry.schema.json`. Enforced by `validate.py` and checked during repo sync for compatibility.

**Do not modify this file.** Changing it breaks compatibility with all community brain repos.
