# Quickstart

## Prerequisites

- Python 3.10+
- `pip install jsonschema`

---

## 5 steps to get started

### Step 1 — Get NEXUSBRAIN_GLOBAL

Clone or download `NEXUSBRAIN_GLOBAL` to a **permanent location outside your projects**:

```
git clone https://github.com/you/NEXUSBRAIN_GLOBAL C:/brains/NEXUSBRAIN_GLOBAL
```

Or copy the `NEXUSBRAIN_GLOBAL/` folder anywhere permanent on your machine.

### Step 2 — Copy PROJECT_TEMPLATE into your project

```
xcopy /E /I PROJECT_TEMPLATE\. your-project\
```

This adds:
- `.nexusbrain` — config pointing to the global brain
- `.ai_cache/CURRENT.md` — project context for AI
- `BRAIN/ai_memory.local.json` — local knowledge overrides
- `.github/copilot-instructions.md` — automatic AI instructions

### Step 3 — Set global_path in .nexusbrain

Open `.nexusbrain` in your project and set the path to your `NEXUSBRAIN_GLOBAL` folder:

```json
{
  "global_path": "C:/brains/NEXUSBRAIN_GLOBAL",
  "relevant_categories": ["frameworks", "patterns", "pitfalls"],
  "global_token": null
}
```

See [configuration.md](configuration.md) for all options.

### Step 4 — Fill in .ai_cache/CURRENT.md

Edit `.ai_cache/CURRENT.md` with your project details:

```
- Project: MyApp
- Stack: Python + FastAPI + PostgreSQL
- Patterns: repository pattern, service layer
- Integrations: Redis, Stripe
- Relevant categories: frameworks, patterns, integrations, pitfalls
```

### Step 5 — Update copilot-instructions.md

Open `.github/copilot-instructions.md` and replace `<GLOBAL>` with your `global_path` from step 3:

```
python C:/brains/NEXUSBRAIN_GLOBAL/nexus.py query "..."
```

**Done.** AI will now automatically query NexusBrain before answering technical questions.

---

## Verify it works

Run from the `NEXUSBRAIN_GLOBAL/` directory:

```
python nexus.py
```

Choose `[3] Validate` — it should pass with no errors.

To test a query:

```
python nexus.py query "FastAPI"
```

Returns `{}` if the brain is empty, or matching entries if populated.
