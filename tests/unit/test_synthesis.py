"""Unit tests for digest formatting."""

from __future__ import annotations

from professor_claude_ai.agents.synthesis import _format_digest
from professor_claude_ai.state import (
    ClaimWithProvenance,
    DeepReadReport,
    TriageDecision,
)


def test_empty_digest_has_correct_structure() -> None:
    digest = _format_digest(
        run_date="2026-05-06",
        deep_reads=[],
        triage_decisions=[],
        n_candidates=0,
    )
    assert "Daily Digest" in digest
    assert "2026-05-06" in digest
    assert "No deep reads tonight" in digest


def test_digest_with_deep_reads_includes_all_sections() -> None:
    report = DeepReadReport(
        arxiv_id="2401.12345",
        background="prior work x",
        core_innovation="they propose y",
        methodology_strengths=["clean ablation"],
        methodology_weaknesses=["small N"],
        results_summary="3% gain on benchmark Z",
        relevance_to_user="connects to your tool-use interest",
        connections=["2312.99999"],
        key_equations_or_diagrams=["Eq. 4"],
        claims=[
            ClaimWithProvenance(
                claim="3% improvement over baseline",
                source_section="Table 2",
                confidence="high",
            )
        ],
        overall_confidence="high",
    )
    triage = [
        TriageDecision(
            arxiv_id="2401.12345",
            decision="deep_read",
            score=0.9,
            reason="match",
            matched_keywords=["agent"],
        ),
        TriageDecision(
            arxiv_id="2401.55555",
            decision="skim",
            score=0.4,
            reason="match",
            matched_keywords=["tool"],
        ),
    ]
    digest = _format_digest(
        run_date="2026-05-06",
        deep_reads=[report],
        triage_decisions=triage,
        n_candidates=42,
    )
    assert "2401.12345" in digest
    assert "they propose y" in digest
    assert "## Skims" in digest
    assert "2401.55555" in digest
    assert "Surveyed 42" in digest
