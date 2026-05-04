"""Tests for KnowledgeEntry model."""

import pytest

from nexusbrain.models import KnowledgeEntry


SAMPLE_DATA = {
    "id": "coding/test-entry",
    "title": "Test Entry",
    "category": "coding",
    "description": "A test knowledge entry.",
    "content": "This is the content of the test entry.",
    "tags": ["test", "coding"],
    "examples": ["example one", "example two"],
    "source": "https://example.com",
}


def make_entry(**overrides) -> KnowledgeEntry:
    data = {**SAMPLE_DATA, **overrides}
    return KnowledgeEntry.from_dict(data)


class TestKnowledgeEntryFromDict:
    def test_all_fields_populated(self):
        entry = make_entry()
        assert entry.id == "coding/test-entry"
        assert entry.title == "Test Entry"
        assert entry.category == "coding"
        assert entry.description == "A test knowledge entry."
        assert entry.content == "This is the content of the test entry."
        assert entry.tags == ["test", "coding"]
        assert entry.examples == ["example one", "example two"]
        assert entry.source == "https://example.com"

    def test_optional_fields_default_to_empty(self):
        data = {k: v for k, v in SAMPLE_DATA.items() if k not in ("tags", "examples", "source")}
        entry = KnowledgeEntry.from_dict(data)
        assert entry.tags == []
        assert entry.examples == []
        assert entry.source is None

    def test_missing_required_field_raises(self):
        data = {k: v for k, v in SAMPLE_DATA.items() if k != "title"}
        with pytest.raises(KeyError):
            KnowledgeEntry.from_dict(data)


class TestKnowledgeEntryToDict:
    def test_round_trip(self):
        entry = make_entry()
        assert KnowledgeEntry.from_dict(entry.to_dict()).to_dict() == entry.to_dict()

    def test_all_keys_present(self):
        entry = make_entry()
        d = entry.to_dict()
        for key in ("id", "title", "category", "description", "content", "tags", "examples", "source"):
            assert key in d


class TestToCompactText:
    def test_contains_id_and_title(self):
        entry = make_entry()
        text = entry.to_compact_text()
        assert entry.id in text
        assert entry.title in text

    def test_contains_content(self):
        entry = make_entry()
        assert entry.content in entry.to_compact_text()

    def test_contains_examples_when_present(self):
        entry = make_entry()
        text = entry.to_compact_text()
        assert "example one" in text
        assert "example two" in text

    def test_no_examples_section_when_empty(self):
        entry = make_entry(examples=[])
        assert "Examples:" not in entry.to_compact_text()
