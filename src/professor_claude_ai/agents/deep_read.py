"""Deep-read agent — produces structured analysis of papers marked deep_read.

v0.1: single Claude call per paper with structured output. No verification pass yet.
v0.4: migrate to RLM-style recursive reading + add verification pass that
cross-checks numerical claims against source.
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_anthropic import ChatAnthropic

from professor_claude_ai.config import get_settings
from professor_claude_ai.config.prompts import DEEP_READ_SYSTEM_PROMPT
from professor_claude_ai.state import (
    DeepReadReport,
    PaperMetadata,
    ProfessorState,
    TriageDecision,
)
from professor_claude_ai.tools.paper_tools import fetch_paper_text

logger = logging.getLogger(__name__)


def _deep_read_one(
    paper: PaperMetadata,
    you_interests: list[str],
    you_courses: list[str],
) -> DeepReadReport | None:
    """Run one deep read against Claude with structured output."""
    settings = get_settings()
    text = fetch_paper_text(paper.pdf_url)
    if not text:
        logger.warning("deep_read: failed to fetch %s", paper.arxiv_id)
        return None

    # Truncate to keep context size reasonable for v0.1.
    # v0.4 will use RLM to handle full-length papers without context rot.
    max_chars = 150_000
    if len(text) > max_chars:
        logger.info(
            "deep_read: %s truncated from %d to %d chars",
            paper.arxiv_id,
            len(text),
            max_chars,
        )
        text = text[:max_chars]

    # Note: we deliberately do NOT pass `temperature` because Claude Opus 4.7
    # deprecated the parameter. The model's default sampling behavior is
    # appropriate for structured-output tasks like this one.
    llm = ChatAnthropic(
        model_name=settings.deep_read_model,
        max_tokens_to_sample=16384,
        timeout=120.0,
        stop=None,
    )
    structured_llm = llm.with_structured_output(DeepReadReport)

    user_content = (
        f"Paper: {paper.title}\n"
        f"Authors: {', '.join(paper.authors)}\n"
        f"arXiv ID: {paper.arxiv_id}\n\n"
        f"User's declared interests: {', '.join(you_interests)}\n"
        f"User's current courses: {', '.join(you_courses)}\n\n"
        f"Full paper text follows.\n\n---\n\n{text}"
    )

    try:
        report = structured_llm.invoke(
            [
                ("system", DEEP_READ_SYSTEM_PROMPT),
                ("human", user_content),
            ]
        )
    except Exception as e:
        import traceback

        logger.error("deep_read: claude call failed for %s: %s", paper.arxiv_id, e)
        logger.error("exception type: %s", type(e).__name__)
        logger.error("exception module: %s", type(e).__module__)
        logger.error("traceback:\n%s", traceback.format_exc())
        # Walk the cause chain — langchain wraps real errors
        cause = e.__cause__
        depth = 0
        while cause and depth < 5:
            logger.error("caused by [%d]: %s: %s", depth, type(cause).__name__, cause)
            cause = cause.__cause__
            depth += 1
        return None
    # Ensure arxiv_id matches (model might fill it differently)
    if isinstance(report, DeepReadReport):
        report.arxiv_id = paper.arxiv_id
        return report
    logger.warning("deep_read: unexpected return type: %r", type(report))
    return None


def deep_read_node(state: ProfessorState) -> dict[str, Any]:
    """Process all papers triaged as deep_read."""
    decisions: list[TriageDecision] = state.get("triage_decisions", [])
    candidates: list[PaperMetadata] = state.get("candidate_papers", [])
    you = state.get("you_model_snapshot")
    if you is None:
        raise RuntimeError("you_model_snapshot must be set before deep_read runs")

    by_id = {p.arxiv_id: p for p in candidates}
    targets = [d for d in decisions if d.decision == "deep_read"]
    logger.info("deep_read: processing %d papers", len(targets))

    reports: list[DeepReadReport] = []
    for d in targets:
        paper = by_id.get(d.arxiv_id)
        if paper is None:
            logger.warning("deep_read: no metadata for %s", d.arxiv_id)
            continue
        report = _deep_read_one(
            paper=paper,
            you_interests=you.declared_interests,
            you_courses=you.current_courses,
        )
        if report is not None:
            reports.append(report)

    return {
        "deep_reads": reports,
        "current_agent": "deep_read_agent",
        "agent_history": [*state.get("agent_history", []), "deep_read_agent"],
    }
