"""Ingestion agent — pulls candidate papers from configured sources.

v0.1: arXiv only, single-day window, keyword pre-filter from settings.
v0.2: add alphaXiv, HF Daily Papers, lab blogs (RSS), OpenReview.
"""

from __future__ import annotations

import logging
from typing import Any

from professor_claude_ai.config import get_settings
from professor_claude_ai.state import ProfessorState
from professor_claude_ai.tools.arxiv_tools import search_arxiv_recent

logger = logging.getLogger(__name__)


def ingestion_node(state: ProfessorState) -> dict[str, Any]:
    """Pull candidate papers from arXiv. State update only — no LLM call.

    Pure function over settings; deterministic-ish (arXiv results vary slightly).
    """
    settings = get_settings()
    keywords = settings.keyword_list
    logger.info("ingestion: searching arxiv with keywords=%s", keywords)

    papers = search_arxiv_recent(
        keywords=keywords,
        days_back=2,
        max_results=50,
    )
    logger.info("ingestion: %d candidate papers", len(papers))

    return {
        "candidate_papers": papers,
        "current_agent": "ingestion_agent",
        "agent_history": [*state.get("agent_history", []), "ingestion_agent"],
    }
