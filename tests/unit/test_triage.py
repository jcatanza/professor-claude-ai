"""Unit tests for triage scoring."""

from __future__ import annotations

from professor_claude_ai.agents.triage import _decide, _score_paper
from professor_claude_ai.state import PaperMetadata, YouModelSnapshot


def test_score_paper_no_keywords_no_interests_zero(sample_paper: PaperMetadata) -> None:
    """With both keywords AND declared interests empty, score should be 0."""
    you = YouModelSnapshot(
        declared_interests=[],
        current_courses=[],
        current_reading=[],
        recent_thumbs_up_arxiv_ids=[],
        recent_thumbs_down_arxiv_ids=[],
    )
    score, matched = _score_paper(sample_paper, keywords=[], you=you)
    assert score == 0.0
    assert matched == []


def test_score_paper_interest_bonus_independent_of_keywords(
    sample_paper: PaperMetadata, sample_you_snapshot: YouModelSnapshot
) -> None:
    """Even with no keywords, a declared interest matching the abstract gives a small bonus."""
    score, _ = _score_paper(sample_paper, keywords=[], you=sample_you_snapshot)
    # sample_you_snapshot includes "agents", which appears in the sample paper's text
    assert score > 0.0
    assert score <= 0.2  # only the interest_bonus should fire, no keyword/title bonus


def test_score_paper_keyword_in_title(
    sample_paper: PaperMetadata, sample_you_snapshot: YouModelSnapshot
) -> None:
    # "agent" appears in the title and abstract; "harness" in the title
    score, matched = _score_paper(
        sample_paper, keywords=["agent", "harness"], you=sample_you_snapshot
    )
    assert score > 0.0
    assert "agent" in matched
    assert "harness" in matched


def test_thumbs_down_zeroes_score(sample_paper: PaperMetadata) -> None:
    you = YouModelSnapshot(
        declared_interests=[],
        current_courses=[],
        current_reading=[],
        recent_thumbs_up_arxiv_ids=[],
        recent_thumbs_down_arxiv_ids=[sample_paper.arxiv_id],
    )
    score, _ = _score_paper(sample_paper, keywords=["agent"], you=you)
    assert score == 0.0


def test_decide_thresholds() -> None:
    assert _decide(0.0) == "skip"
    assert _decide(0.24) == "skip"
    assert _decide(0.25) == "skim"
    assert _decide(0.59) == "skim"
    assert _decide(0.60) == "deep_read"
    assert _decide(1.0) == "deep_read"
