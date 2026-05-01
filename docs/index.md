# NexusBrain Documentation

NexusBrain is a two-layer AI memory system that reduces token usage and hallucinations by storing reusable knowledge in a structured, searchable brain. Instead of loading thousands of tokens of context, AI calls `nexus.py query` and receives only the relevant entries (~150 tokens).

## How it works

```
You write a prompt
      ↓
AI runs: python <global_path>/nexus.py query "<key terms>"
      ↓
Script searches global brain + local brain
Returns only matching entries (typically < 200 tokens)
      ↓
AI answers using real stored knowledge
      ↓
AI saves new reusable knowledge back to the brain
```

## Two memory layers

| Layer | Location | Purpose |
|-------|----------|---------|
| Global brain | `NEXUSBRAIN_GLOBAL/BRAIN/` | Reusable knowledge across all projects |
| Local brain | `<project>/BRAIN/ai_memory.local.json` | Project-specific overrides |

Local entries always override global entries with the same key.

## Documentation

| File | Contents |
|------|----------|
| [quickstart.md](quickstart.md) | Get started in 5 steps |
| [configuration.md](configuration.md) | `.nexusbrain` config file reference |
| [ai-protocol.md](ai-protocol.md) | How AI uses NexusBrain automatically |
| [commands.md](commands.md) | All `nexus.py` commands and menu options |
| [repos-and-sync.md](repos-and-sync.md) | External repos, priorities, and sync |
| [versioning.md](versioning.md) | SHA tracking and update checking |
| [conflicts.md](conflicts.md) | Auto and interactive conflict resolution |
| [contributing.md](contributing.md) | How to share your brain with others |
| [schema.md](schema.md) | Entry format reference |
