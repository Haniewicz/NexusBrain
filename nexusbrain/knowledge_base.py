"""Core KnowledgeBase class for NexusBrain."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

import yaml

from nexusbrain.models import KnowledgeEntry


_DEFAULT_KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"


class KnowledgeBase:
    """Loads, stores, and retrieves :class:`KnowledgeEntry` objects.

    Parameters
    ----------
    knowledge_dir:
        Directory that contains category sub-folders with YAML knowledge
        files.  Defaults to the ``knowledge/`` directory bundled with this
        repository.
    """

    def __init__(self, knowledge_dir: Optional[str | Path] = None) -> None:
        self._dir = Path(knowledge_dir) if knowledge_dir else _DEFAULT_KNOWLEDGE_DIR
        self._entries: List[KnowledgeEntry] = []
        self.load()

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load(self) -> None:
        """(Re-)load all knowledge entries from *knowledge_dir*."""
        self._entries = []
        if not self._dir.exists():
            return
        for yaml_file in sorted(self._dir.rglob("*.yaml")):
            self._load_file(yaml_file)

    def _load_file(self, path: Path) -> None:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if not data:
            return
        # A file may contain a single entry (dict) or a list of entries.
        if isinstance(data, dict):
            data = [data]
        for raw in data:
            try:
                entry = KnowledgeEntry.from_dict(raw)
                self._entries.append(entry)
            except (KeyError, TypeError) as exc:
                raise ValueError(
                    f"Invalid knowledge entry in {path}: {exc}"
                ) from exc

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def all_entries(self) -> List[KnowledgeEntry]:
        """Return all loaded knowledge entries."""
        return list(self._entries)

    def get(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Return the entry with the given *entry_id*, or ``None``."""
        for entry in self._entries:
            if entry.id == entry_id:
                return entry
        return None

    def search(
        self,
        query: str,
        *,
        category: Optional[str] = None,
        max_results: int = 10,
    ) -> List[KnowledgeEntry]:
        """Search entries by keyword.

        Matches are ranked by the number of query terms found in the entry's
        *title*, *description*, *content*, and *tags*.  The search is
        case-insensitive.

        Parameters
        ----------
        query:
            Space-separated search terms.
        category:
            When provided, restrict results to this category.
        max_results:
            Maximum number of entries to return.
        """
        terms = [t.lower() for t in query.split() if t]
        if not terms:
            candidates = self._entries
            if category:
                candidates = [e for e in candidates if e.category == category]
            return candidates[:max_results]

        scored: List[tuple[int, KnowledgeEntry]] = []
        for entry in self._entries:
            if category and entry.category != category:
                continue
            score = self._score(entry, terms)
            if score > 0:
                scored.append((score, entry))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [entry for _, entry in scored[:max_results]]

    @staticmethod
    def _score(entry: KnowledgeEntry, terms: List[str]) -> int:
        """Return a relevance score for *entry* against *terms*."""
        haystack = " ".join(
            [
                entry.title,
                entry.description,
                entry.content,
                " ".join(entry.tags),
                entry.id,
            ]
        ).lower()
        return sum(1 for term in terms if term in haystack)

    def build_context(
        self,
        query: str,
        *,
        category: Optional[str] = None,
        max_results: int = 5,
    ) -> str:
        """Build a token-efficient context string for injection into AI prompts.

        Retrieves the most relevant knowledge entries for *query* and
        concatenates their compact text representations.  Injecting this
        string into a system prompt allows the AI to reference established
        knowledge without re-deriving it from scratch, reducing token usage.

        Parameters
        ----------
        query:
            Natural-language query describing the current task.
        category:
            Optional category filter.
        max_results:
            Maximum number of entries to include.

        Returns
        -------
        str
            A multi-line string ready to be inserted into a prompt, or an
            empty string if no relevant entries were found.
        """
        entries = self.search(query, category=category, max_results=max_results)
        if not entries:
            return ""
        header = "--- NexusBrain Knowledge ---"
        body = "\n\n".join(e.to_compact_text() for e in entries)
        footer = "--- End of Knowledge ---"
        return "\n".join([header, body, footer])

    # ------------------------------------------------------------------
    # Adding entries at runtime
    # ------------------------------------------------------------------

    def add_entry(self, entry: KnowledgeEntry) -> None:
        """Add a :class:`KnowledgeEntry` to the in-memory store.

        Raises :class:`ValueError` if an entry with the same *id* already
        exists.
        """
        if self.get(entry.id) is not None:
            raise ValueError(f"Entry with id '{entry.id}' already exists.")
        self._entries.append(entry)

    def __len__(self) -> int:
        return len(self._entries)

    def __repr__(self) -> str:  # pragma: no cover
        return f"KnowledgeBase(entries={len(self._entries)}, dir='{self._dir}')"
