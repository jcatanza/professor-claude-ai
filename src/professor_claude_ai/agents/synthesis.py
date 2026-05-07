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

from professor_claude_ai.state import DeepReadReport, ProfessorState, TriageDecision

logger = logging.getLogger(__name__)


def _format_digest(
    run_date: str,
    deep_reads: list[DeepReadReport],
    triage_decisions: list[TriageDecision],
    n_candidates: int,
) -> str:
    """Format the deep-reads + skims into a markdown digest."""
    lines = [
        f"# Professor.Claude.AI — Daily Digest, {run_date}",
        "",
        f"Surveyed {n_candidates} candidate papers. "
        f"Deep-reads: {sum(1 for d in triage_decisions if d.decision == 'deep_read')}. "
        f"Skims: {sum(1 for d in triage_decisions if d.decision == 'skim')}. "
        f"Skipped: {sum(1 for d in triage_decisions if d.decision == 'skip')}.",
        "",
        "---",
        "",
        "## Deep reads",
        "",
    ]

    if not deep_reads:
        lines.append(
            "*No deep reads tonight — triage filter found nothing meeting "
            "the threshold. Consider broadening keywords or reviewing the "
            "skim list below.*"
        )
        lines.append("")
    else:
        for r in deep_reads:
            lines.extend(
                [
                    f"### {r.arxiv_id}",
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
            lines.append(f"- `{d.arxiv_id}` — score {d.score:.2f}, matched {d.matched_keywords}")
        if len(skims) > 20:
            lines.append(f"- *...and {len(skims) - 20} more.*")
        lines.append("")

    return "\n".join(lines)


def synthesis_node(state: ProfessorState) -> dict[str, Any]:
    """Format the daily digest. Emit-to-email/repo handled by post_run hooks."""
    digest = _format_digest(
        run_date=state.get("run_date", "unknown"),
        deep_reads=state.get("deep_reads", []),
        triage_decisions=state.get("triage_decisions", []),
        n_candidates=len(state.get("candidate_papers", [])),
    )
    logger.info("synthesis: digest %d chars", len(digest))
    return {
        "daily_digest": digest,
        "current_agent": "synthesis_agent",
        "agent_history": [*state.get("agent_history", []), "synthesis_agent"],
    }
