"""Synthesis agent — formats the daily digest and emits it.

v0.1: pure-Python digest formatting from the deep-read reports + triage decisions.
No LLM call here in v0.1 — the deep-reads themselves are already digest-ready.
v0.3+: weekly reflective synthesis with LLM ("what shifted this week").

Email and repo-commit delivery are stubbed; wire them up in v0.1.5 once the
spine is verified end-to-end.
"""

from __future__ import annotations

import logging
from typing import Any

from professor_claude_ai.state import (
    DeepReadReport,
    PaperMetadata,
    ProfessorState,
    TriageDecision,
)

logger = logging.getLogger(__name__)


def _format_digest(
    run_date: str,
    deep_reads: list[DeepReadReport],
    triage_decisions: list[TriageDecision],
    candidate_papers: list[PaperMetadata],
    n_candidates: int,
) -> str:
    """Format the deep-reads + skims into a markdown digest.

    Three empty-deep-reads cases are distinguished so the user can tell
    whether the pipeline produced nothing because:
      (a) there were no candidates at all (upstream fetch issue)
      (b) triage promoted candidates but the deep_read step failed
      (c) triage promoted nothing — filter was the binding constraint
    """
    # arxiv_id -> title lookup so we can show titles alongside ids
    title_by_id = {p.arxiv_id: p.title for p in candidate_papers}

    n_deep_promoted = sum(1 for d in triage_decisions if d.decision == "deep_read")
    n_skim = sum(1 for d in triage_decisions if d.decision == "skim")
    n_skip = sum(1 for d in triage_decisions if d.decision == "skip")

    lines = [
        f"# Professor.Claude.AI — Daily Digest, {run_date}",
        "",
        f"Surveyed {n_candidates} candidate papers. "
        f"Deep-reads: {len(deep_reads)} produced ({n_deep_promoted} promoted by triage). "
        f"Skims: {n_skim}. "
        f"Skipped: {n_skip}.",
        "",
        "---",
        "",
        "## Deep reads",
        "",
    ]

    if not deep_reads:
        # Three distinct empty cases (B)
        if n_candidates == 0:
            lines.append(
                "*No candidates fetched — upstream arXiv fetch returned nothing. "
                "Check the fetch step in the run log.*"
            )
        elif n_deep_promoted > 0:
            # Triage promoted some, but deep_read step produced none.
            lines.append(
                f"*Triage promoted {n_deep_promoted} paper(s) for deep reading, "
                "but no deep-read reports were produced. The deep_read step "
                "likely failed for all promoted papers. Check the run log for "
                "PDF/API errors.*"
            )
        else:
            # Triage promoted nothing. Surface the top scores.
            top = sorted(triage_decisions, key=lambda d: d.score, reverse=True)[:3]
            lines.append("*Triage promoted nothing for deep reading. Top candidate scores:*")
            lines.append("")
            for d in top:
                title = title_by_id.get(d.arxiv_id, "(title unavailable)")
                lines.append(
                    f"- `{d.arxiv_id}` — score {d.score:.2f}, "
                    f"matched {d.matched_keywords} — {title}"
                )
            lines.append("")
            lines.append(
                "*Consider lowering the deep_read threshold, broadening keywords, "
                "or expanding declared interests in the You-Model.*"
            )
        lines.append("")
    else:
        for r in deep_reads:
            title = title_by_id.get(r.arxiv_id, "(title unavailable)")
            lines.extend(
                [
                    f"### {r.arxiv_id} — {title}",
                    "",
                    f"**Background.** {r.background}",
                    "",
                    f"**Core innovation.** {r.core_innovation}",
                    "",
                    "**Methodology — strengths:**",
                    *[f"- {s}" for s in r.methodology_strengths],
                    "",
                    "**Methodology — weaknesses:**",
                    *[f"- {w}" for w in r.methodology_weaknesses],
                    "",
                    f"**Results.** {r.results_summary}",
                    "",
                    f"**Why this is on your radar.** {r.relevance_to_user}",
                    "",
                    f"**Confidence:** {r.overall_confidence}",
                    "",
                    "**Connections:**",
                    *[f"- {c}" for c in (r.connections or ["(none yet)"])],
                    "",
                    "---",
                    "",
                ]
            )

    skims = [d for d in triage_decisions if d.decision == "skim"]
    if skims:
        lines.extend(
            [
                "## Skims",
                "",
            ]
        )
        for d in skims[:20]:  # cap; full list is in the run log
            title = title_by_id.get(d.arxiv_id, "(title unavailable)")
            lines.append(
                f"- `{d.arxiv_id}` — score {d.score:.2f}, matched {d.matched_keywords} — {title}"
            )
        if len(skims) > 20:
            lines.append(f"- *...and {len(skims) - 20} more.*")
        lines.append("")

    return "\n".join(lines)


def synthesis_node(state: ProfessorState) -> dict[str, Any]:
    """Format the daily digest. Emit-to-email/repo handled by post_run hooks."""
    candidate_papers = state.get("candidate_papers", [])
    digest = _format_digest(
        run_date=state.get("run_date", "unknown"),
        deep_reads=state.get("deep_reads", []),
        triage_decisions=state.get("triage_decisions", []),
        candidate_papers=candidate_papers,
        n_candidates=len(candidate_papers),
    )
    logger.info("synthesis: digest %d chars", len(digest))
    return {
        "daily_digest": digest,
        "current_agent": "synthesis_agent",
        "agent_history": [*state.get("agent_history", []), "synthesis_agent"],
    }
