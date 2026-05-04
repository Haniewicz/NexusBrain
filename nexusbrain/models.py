"""Data models for NexusBrain knowledge entries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class KnowledgeEntry:
    """A single knowledge entry in the NexusBrain knowledge base.

    Attributes:
        id: Unique identifier for the entry (e.g. ``coding/python-list-comp``).
        title: Short human-readable title.
        category: Top-level category (e.g. ``coding``, ``math``, ``writing``).
        description: One-line summary of the entry.
        content: The full knowledge content shown to the AI.
        tags: List of searchable tags.
        examples: Optional illustrative examples.
        source: Optional attribution / URL.
    """

    id: str
    title: str
    category: str
    description: str
    content: str
    tags: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    source: Optional[str] = None

    # ------------------------------------------------------------------
    # Token-efficient representation helpers
    # ------------------------------------------------------------------

    def to_compact_text(self) -> str:
        """Return a concise text representation suitable for AI context injection.

        The compact format deliberately avoids redundant whitespace so that
        fewer tokens are consumed when this entry is added to a prompt.
        """
        lines = [
            f"[{self.id}] {self.title}",
            self.content,
        ]
        if self.examples:
            lines.append("Examples: " + " | ".join(self.examples))
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Serialise the entry to a plain dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "content": self.content,
            "tags": self.tags,
            "examples": self.examples,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeEntry":
        """Deserialise a ``KnowledgeEntry`` from a plain dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            category=data["category"],
            description=data["description"],
            content=data["content"],
            tags=data.get("tags", []),
            examples=data.get("examples", []),
            source=data.get("source"),
        )
