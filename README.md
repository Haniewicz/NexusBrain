# NexusBrain

> **Global AI knowledge base to improve performance and decrease token usage.  
> Everyone can contribute.**

NexusBrain is a community-driven, YAML-powered knowledge base that can be
injected into AI prompts. By storing concise, reusable knowledge entries and
fetching only the ones relevant to the current task, you can:

- **Improve AI accuracy** — ground answers in established knowledge.
- **Reduce token usage** — include only the relevant snippets instead of
  repeating explanations from scratch.
- **Enable community contributions** — anyone can add entries via a pull
  request.

---

## Quick Start

```bash
pip install nexusbrain       # or: pip install -e . from this repo
```

```python
from nexusbrain import KnowledgeBase

kb = KnowledgeBase()         # loads all bundled knowledge entries

# Search for relevant entries
results = kb.search("python performance")
for entry in results:
    print(f"[{entry.id}] {entry.title}")
    print(entry.content)

# Build a token-efficient context string ready for prompt injection
context = kb.build_context("reduce token usage", max_results=3)
print(context)
```

### Example output

```
--- NexusBrain Knowledge ---
[prompting/reduce-token-usage] Strategies to Reduce Token Usage
1. Use bullet points instead of full sentences …

[prompting/chain-of-thought] Chain-of-Thought Prompting
Append "Think step by step." …
--- End of Knowledge ---
```

Paste `context` at the top of your system prompt, and the AI will reference
the included knowledge without needing to re-derive it.

---

## Repository Layout

```
NexusBrain/
├── nexusbrain/               # Python package
│   ├── __init__.py
│   ├── knowledge_base.py     # KnowledgeBase class
│   └── models.py             # KnowledgeEntry dataclass
├── knowledge/                # Community knowledge entries (YAML)
│   ├── coding/
│   ├── math/
│   ├── writing/
│   ├── prompting/
│   └── general/
├── tests/                    # Pytest test suite
├── CONTRIBUTING.md
├── pyproject.toml
└── requirements.txt
```

---

## Knowledge Entry Format

Each YAML file may contain one entry (a mapping) or a list of entries:

```yaml
- id: coding/python-list-comprehension   # <category>/<slug>  (unique)
  title: Python List Comprehensions
  category: coding
  description: Concise syntax for building lists with optional filtering.
  content: >
    Use `[expr for item in iterable if condition]` instead of a for-loop …
  tags: [python, list, comprehension, performance]
  examples:
    - "squares = [x**2 for x in range(10)]"
  source: https://docs.python.org/3/tutorial/datastructures.html  # optional
```

**Required fields:** `id`, `title`, `category`, `description`, `content`  
**Optional fields:** `tags`, `examples`, `source`

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

Short version:

1. Fork the repository.
2. Add or edit a YAML file inside the appropriate `knowledge/<category>/`
   directory (or create a new category folder).
3. Run `pip install -r requirements-dev.txt` then `pytest` to verify your entry is valid.
4. Open a pull request — that's it!

---

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest
```

---

## License

MIT
