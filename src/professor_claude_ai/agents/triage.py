"""Triage agent — decides skip / skim / deep_read for each candidate paper.

v0.1: simple keyword scoring + hard cap from settings. No LLM call (cheap).
v0.2: add local SLM scoring (informed by Manning SLM book).
v0.3: incorporate the You-Model and a learned taste model from feedback.
"""

from __future__ import annotations

import logging
from typing import Any

from professor_claude_ai.config import get_settings
from professor_claude_ai.state import (
    PaperMetadata,
    ProfessorState,
    TriageDecision,
    YouModelSnapshot,
)

logger = logging.getLogger(__name__)


def _score_paper(
    paper: PaperMetadata,
    keywords: list[str],
    you: YouModelSnapshot,
) -> tuple[float, list[str]]:
    """Score a paper 0.0-1.0 by keyword match in title and abstract.

    Bonus weight if title matches (vs only abstract) and if the paper appears
    in the user's declared interests verbatim.
    """
    text = (paper.title + " " + paper.abstract).lower()
    title_lower = paper.title.lower()
    matched = [k for k in keywords if k in text]

    base_score = min(1.0, len(matched) * 0.25)
    title_bonus = 0.2 if any(k in title_lower for k in matched) else 0.0
    interest_bonus = (
        0.15 if any(interest.lower() in text for interest in you.declared_interests) else 0.0
    )
    # Penalize papers the user has already thumbed-down (similar arxiv_id heuristic
    # is naive; v0.3 will use embeddings)
    penalty = 0.0
    if paper.arxiv_id in you.recent_thumbs_down_arxiv_ids:
        penalty = 1.0  # hard skip

    score = max(0.0, min(1.0, base_score + title_bonus + interest_bonus - penalty))
    return score, matched


def _decide(score: float) -> str:
    """Map score to skip / skim / deep_read."""
    if score >= 0.45:
        return "deep_read"
    if score >= 0.25:
        return "skim"
    return "skip"


def triage_node(state: ProfessorState) -> dict[str, Any]:
    """Score each candidate paper and assign a triage decision.

    Hard cap on deep_reads from settings (anti-overload).
    """
    settings = get_settings()
    candidates = state.get("candidate_papers", [])
    you = state.get("you_model_snapshot")
    if you is None:
        raise RuntimeError("you_model_snapshot must be set before triage runs")

    keywords = settings.keyword_list

    decisions: list[TriageDecision] = []
    for paper in candidates:
        score, matched = _score_paper(paper, keywords, you)
        decision = _decide(score)
        decisions.append(
            TriageDecision(
                arxiv_id=paper.arxiv_id,
                decision=decision,
                score=score,
                reason=f"keyword score={score:.2f}; matched={matched}",
                matched_keywords=matched,
            )
        )

    # Apply hard cap on deep_reads — keep top N by score, demote rest to skim
    deep_reads = sorted(
        [d for d in decisions if d.decision == "deep_read"],
        key=lambda d: d.score,
        reverse=True,
    )
    if len(deep_reads) > settings.max_deep_reads_per_run:
        cutoff_idx = settings.max_deep_reads_per_run
        for d in deep_reads[cutoff_idx:]:
            d.decision = "skim"
            d.reason += f" (demoted: max_deep_reads_per_run={settings.max_deep_reads_per_run})"

    n_deep = sum(1 for d in decisions if d.decision == "deep_read")
    n_skim = sum(1 for d in decisions if d.decision == "skim")
    n_skip = sum(1 for d in decisions if d.decision == "skip")
    logger.info(
        "triage: %d deep_read, %d skim, %d skip (of %d candidates)",
        n_deep,
        n_skim,
        n_skip,
        len(candidates),
    )

    return {
        "triage_decisions": decisions,
        "current_agent": "triage_agent",
        "agent_history": [*state.get("agent_history", []), "triage_agent"],
    }
