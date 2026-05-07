"""Unit tests for the YouModel."""

from __future__ import annotations

from pathlib import Path

import pytest

from professor_claude_ai.memory.you_model import YouModel


def test_you_model_creates_default_on_first_use(tmp_you_model_path: Path) -> None:
    assert not tmp_you_model_path.exists()
    YouModel(tmp_you_model_path)
    assert tmp_you_model_path.exists()


def test_snapshot_contains_declared_fields(tmp_you_model_path: Path) -> None:
    you = YouModel(tmp_you_model_path)
    snap = you.snapshot()
    assert snap.declared_interests  # default seeds these
    assert snap.current_courses
    assert snap.current_reading


def test_record_feedback_persists(tmp_you_model_path: Path) -> None:
    you = YouModel(tmp_you_model_path)
    you.record_feedback("2401.12345", "up", "great paper")
    you.record_feedback("2401.99999", "down", "off-topic")
    snap = you.snapshot()
    assert "2401.12345" in snap.recent_thumbs_up_arxiv_ids
    assert "2401.99999" in snap.recent_thumbs_down_arxiv_ids


def test_record_feedback_rejects_invalid_vote(tmp_you_model_path: Path) -> None:
    you = YouModel(tmp_you_model_path)
    with pytest.raises(ValueError, match="vote must be"):
        you.record_feedback("2401.12345", "maybe")
