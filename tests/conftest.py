"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from professor_claude_ai.state import (
    PaperMetadata,
    YouModelSnapshot,
)


@pytest.fixture
def sample_paper() -> PaperMetadata:
    return PaperMetadata(
        arxiv_id="2401.99999",
        title="A Survey of LLM Agents and Tool Use Harnesses",
        authors=["Alice Researcher", "Bob Coauthor"],
        abstract=(
            "We survey recent work on LLM-based agents and the tool-use harnesses "
            "that enable them. We identify three core architectural patterns and "
            "evaluate them on long-horizon tasks."
        ),
        primary_category="cs.AI",
        submitted_date="2024-01-31",
        pdf_url="https://arxiv.org/pdf/2401.99999",
        abs_url="https://arxiv.org/abs/2401.99999",
    )


@pytest.fixture
def sample_you_snapshot() -> YouModelSnapshot:
    return YouModelSnapshot(
        declared_interests=["agents", "tool use", "harness"],
        current_courses=["LLMs Theory and Practice"],
        current_reading=["Manning AI Agents"],
        recent_thumbs_up_arxiv_ids=[],
        recent_thumbs_down_arxiv_ids=[],
    )


@pytest.fixture
def tmp_you_model_path(tmp_path: Path) -> Path:
    return tmp_path / "you_model.json"
