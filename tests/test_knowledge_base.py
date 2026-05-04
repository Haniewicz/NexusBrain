"""Tests for KnowledgeBase."""

from pathlib import Path

import pytest
import yaml

from nexusbrain.knowledge_base import KnowledgeBase
from nexusbrain.models import KnowledgeEntry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_kb_dir(tmp_path: Path) -> Path:
    """Create a minimal knowledge directory with a couple of YAML entries."""
    cat_dir = tmp_path / "coding"
    cat_dir.mkdir()
    entries = [
        {
            "id": "coding/python-tips",
            "title": "Python Tips",
            "category": "coding",
            "description": "Useful Python tips.",
            "content": "Use list comprehensions and generators for efficiency.",
            "tags": ["python", "performance"],
            "examples": ["[x*2 for x in range(5)]"],
        },
        {
            "id": "coding/git-basics",
            "title": "Git Basics",
            "category": "coding",
            "description": "Git fundamentals.",
            "content": "Commit often, write meaningful commit messages.",
            "tags": ["git", "version-control"],
            "examples": ["git commit -m 'feat: add login page'"],
        },
    ]
    (cat_dir / "coding.yaml").write_text(yaml.dump(entries), encoding="utf-8")

    math_dir = tmp_path / "math"
    math_dir.mkdir()
    math_entries = [
        {
            "id": "math/algebra",
            "title": "Algebra Basics",
            "category": "math",
            "description": "Fundamental algebra rules.",
            "content": "Solve for x: isolate the variable step by step.",
            "tags": ["math", "algebra"],
            "examples": ["2x = 6 → x = 3"],
        }
    ]
    (math_dir / "math.yaml").write_text(yaml.dump(math_entries), encoding="utf-8")
    return tmp_path


@pytest.fixture()
def kb(tmp_kb_dir: Path) -> KnowledgeBase:
    return KnowledgeBase(knowledge_dir=tmp_kb_dir)


# ---------------------------------------------------------------------------
# Loading tests
# ---------------------------------------------------------------------------


class TestKnowledgeBaseLoad:
    def test_loads_all_entries(self, kb: KnowledgeBase):
        assert len(kb) == 3

    def test_empty_dir_loads_zero_entries(self, tmp_path: Path):
        kb = KnowledgeBase(knowledge_dir=tmp_path)
        assert len(kb) == 0

    def test_nonexistent_dir_loads_zero_entries(self, tmp_path: Path):
        kb = KnowledgeBase(knowledge_dir=tmp_path / "does_not_exist")
        assert len(kb) == 0

    def test_invalid_entry_raises_value_error(self, tmp_path: Path):
        bad_dir = tmp_path / "bad"
        bad_dir.mkdir()
        # Missing required 'title' field
        (bad_dir / "bad.yaml").write_text(
            yaml.dump([{"id": "bad/entry", "category": "bad"}]),
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="Invalid knowledge entry"):
            KnowledgeBase(knowledge_dir=tmp_path)

    def test_empty_yaml_file_is_skipped(self, tmp_path: Path):
        cat = tmp_path / "empty_cat"
        cat.mkdir()
        (cat / "empty.yaml").write_text("", encoding="utf-8")
        kb = KnowledgeBase(knowledge_dir=tmp_path)
        assert len(kb) == 0

    def test_single_entry_dict_in_yaml(self, tmp_path: Path):
        """A YAML file with a single dict (not a list) should load one entry."""
        cat = tmp_path / "single"
        cat.mkdir()
        entry = {
            "id": "single/one",
            "title": "Single Entry",
            "category": "single",
            "description": "desc",
            "content": "content",
        }
        (cat / "single.yaml").write_text(yaml.dump(entry), encoding="utf-8")
        kb = KnowledgeBase(knowledge_dir=tmp_path)
        assert len(kb) == 1


# ---------------------------------------------------------------------------
# get() tests
# ---------------------------------------------------------------------------


class TestKnowledgeBaseGet:
    def test_get_existing_entry(self, kb: KnowledgeBase):
        entry = kb.get("coding/python-tips")
        assert entry is not None
        assert entry.title == "Python Tips"

    def test_get_nonexistent_returns_none(self, kb: KnowledgeBase):
        assert kb.get("nonexistent/entry") is None


# ---------------------------------------------------------------------------
# search() tests
# ---------------------------------------------------------------------------


class TestKnowledgeBaseSearch:
    def test_search_returns_relevant_entries(self, kb: KnowledgeBase):
        results = kb.search("python")
        assert any(e.id == "coding/python-tips" for e in results)

    def test_search_with_category_filter(self, kb: KnowledgeBase):
        results = kb.search("basics", category="math")
        assert all(e.category == "math" for e in results)

    def test_search_empty_query_returns_all(self, kb: KnowledgeBase):
        results = kb.search("")
        assert len(results) == 3

    def test_search_no_match_returns_empty(self, kb: KnowledgeBase):
        results = kb.search("zzz_no_match_zzz")
        assert results == []

    def test_search_respects_max_results(self, kb: KnowledgeBase):
        results = kb.search("", max_results=2)
        assert len(results) == 2

    def test_search_case_insensitive(self, kb: KnowledgeBase):
        results_lower = kb.search("python")
        results_upper = kb.search("PYTHON")
        assert {e.id for e in results_lower} == {e.id for e in results_upper}


# ---------------------------------------------------------------------------
# build_context() tests
# ---------------------------------------------------------------------------


class TestBuildContext:
    def test_returns_nonempty_string_for_known_query(self, kb: KnowledgeBase):
        ctx = kb.build_context("python performance")
        assert ctx != ""

    def test_context_contains_header_and_footer(self, kb: KnowledgeBase):
        ctx = kb.build_context("python")
        assert "NexusBrain Knowledge" in ctx
        assert "End of Knowledge" in ctx

    def test_returns_empty_for_unknown_query(self, kb: KnowledgeBase):
        ctx = kb.build_context("zzz_no_match_zzz")
        assert ctx == ""


# ---------------------------------------------------------------------------
# add_entry() tests
# ---------------------------------------------------------------------------


class TestAddEntry:
    def test_add_new_entry(self, kb: KnowledgeBase):
        before = len(kb)
        new_entry = KnowledgeEntry(
            id="general/new-entry",
            title="New Entry",
            category="general",
            description="A fresh entry.",
            content="Content here.",
        )
        kb.add_entry(new_entry)
        assert len(kb) == before + 1
        assert kb.get("general/new-entry") is not None

    def test_add_duplicate_raises(self, kb: KnowledgeBase):
        existing = kb.get("coding/python-tips")
        assert existing is not None
        with pytest.raises(ValueError, match="already exists"):
            kb.add_entry(existing)
