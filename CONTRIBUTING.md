# Contributing to NexusBrain

Thank you for helping grow the global AI knowledge base! 🎉

## Ways to Contribute

- **Add new knowledge entries** — the most impactful contribution.
- **Improve existing entries** — fix errors, add examples, or make content
  more concise.
- **Add a new category** — create a new folder under `knowledge/` and add a
  YAML file.
- **Improve the Python package** — bug fixes, performance improvements, new
  features.

---

## Adding or Editing Knowledge Entries

### File Location

Knowledge is stored as YAML files under `knowledge/<category>/`.  
Each file may contain a **single entry** (a YAML mapping) or a **list of
entries**.

### Entry Schema

```yaml
- id: category/entry-slug          # Required. Unique. Format: <category>/<kebab-slug>
  title: Short Human-Readable Title  # Required
  category: category               # Required. Must match the folder name
  description: One-line summary.   # Required
  content: >                       # Required. The full knowledge text shown to the AI.
    Write concise, factual content. Avoid padding.
    Prefer bullet points and short sentences.
  tags: [tag1, tag2, tag3]         # Optional but recommended for search
  examples:                        # Optional. Short illustrative examples.
    - "example one"
    - "example two"
  source: https://...              # Optional. Attribution or reference URL.
```

### Existing Categories

| Folder | Description |
|---|---|
| `coding/` | Programming, algorithms, software engineering |
| `math/` | Mathematics, statistics, linear algebra |
| `writing/` | Technical writing, documentation, prompt engineering |
| `prompting/` | AI prompt design, token efficiency, LLM best practices |
| `general/` | Reasoning, learning strategies, general knowledge |

To add a **new category**, create `knowledge/<new-category>/<new-category>.yaml`
and set `category: <new-category>` in your entries.

---

## Step-by-Step Guide

1. **Fork** the repository and create a branch:
   ```bash
   git checkout -b knowledge/add-my-entries
   ```

2. **Add or edit** a YAML file in the appropriate `knowledge/<category>/`
   directory.

3. **Install dependencies** and run the tests to make sure your entries are
   valid:
   ```bash
   pip install -r requirements-dev.txt
   pytest
   ```

4. **Verify** your entries load correctly:
   ```python
   from nexusbrain import KnowledgeBase
   kb = KnowledgeBase()
   entry = kb.get("category/your-entry-slug")
   print(entry.to_compact_text())
   ```

5. **Open a pull request** against `master` with a clear title such as
   `knowledge: add Python async/await entry`.

---

## Quality Guidelines

- **Be concise.** Fewer tokens = better performance. Aim for content under
  200 words per entry.
- **Be accurate.** Cite a `source` URL for any non-trivial factual claims.
- **Be neutral.** Avoid opinions; document what is, not what should be.
- **Unique IDs.** Every entry needs a globally unique `id` in the form
  `<category>/<kebab-slug>`.
- **No duplicates.** Search existing entries before adding a new one.

---

## Code Contributions

1. Install the dev environment:
   ```bash
   pip install -r requirements-dev.txt
   pip install -e .
   ```
2. Make your changes and add or update tests in `tests/`.
3. Run `pytest` — all tests must pass.
4. Open a pull request.

---

## Code of Conduct

Be kind, inclusive, and constructive. All contributions are welcome regardless
of experience level.
