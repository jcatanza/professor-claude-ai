"""arXiv search tools.

Query strategy: fetch recent papers by category alone (cheap, well-cached on
arXiv's side), then filter client-side by keywords. This is gentler on arXiv's
rate limiter than a complex multi-clause query and gives us more control over
matching logic.
"""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime, timedelta

import arxiv
from langchain_core.tools import tool

from professor_claude_ai.state import PaperMetadata

logger = logging.getLogger(__name__)


# Default arxiv categories for the agents-and-harnesses subfield (v0.1)
DEFAULT_CATEGORIES = ["cs.AI", "cs.LG", "cs.CL"]


def _result_to_metadata(result: arxiv.Result) -> PaperMetadata:
    """Convert arxiv.Result into our typed PaperMetadata."""
    arxiv_id = result.entry_id.rsplit("/", 1)[-1]
    if "v" in arxiv_id:
        arxiv_id = arxiv_id.rsplit("v", 1)[0]
    return PaperMetadata(
        arxiv_id=arxiv_id,
        title=result.title.strip().replace("\n", " "),
        authors=[a.name for a in result.authors],
        abstract=result.summary.strip().replace("\n", " "),
        primary_category=result.primary_category,
        submitted_date=result.published.date().isoformat(),
        pdf_url=result.pdf_url,
        abs_url=result.entry_id,
    )


def _matches_any_keyword(paper: PaperMetadata, keywords: list[str]) -> bool:
    """True if paper's title or abstract matches any keyword (word-boundary aware).

    Short keywords use word boundaries to avoid false positives
    (e.g. 'react' should not match 'reactor' or 'reaction').
    Longer phrases and hyphenated terms use substring matching.
    """
    if not keywords:
        return True
    text = (paper.title + " " + paper.abstract).lower()
    for kw in keywords:
        kw_lower = kw.lower().strip()
        if not kw_lower:
            continue
        if len(kw_lower) <= 6 and "-" not in kw_lower and " " not in kw_lower:
            pattern = r"\b" + re.escape(kw_lower) + r"\b"
            if re.search(pattern, text):
                return True
        else:
            if kw_lower in text:
                return True
    return False


def search_arxiv_recent(
    keywords: list[str],
    categories: list[str] | None = None,
    days_back: int = 1,
    max_results: int = 50,
) -> list[PaperMetadata]:
    """Search arXiv for recent papers matching any of the given keywords.

    Strategy: fetch by category only, filter client-side by keyword. Lighter
    on arXiv's rate limiter than a complex multi-clause query.

    Args:
        keywords: list of keywords to match in title/abstract (OR semantics)
        categories: arXiv categories (default: cs.AI, cs.LG, cs.CL)
        days_back: only return papers submitted in the last N days
        max_results: cap on results returned after filtering

    Returns:
        List of PaperMetadata, deduplicated by arxiv_id.
    """
    cats = categories or DEFAULT_CATEGORIES
    cutoff = datetime.now(UTC) - timedelta(days=days_back)

    # Simple category-only query — arXiv handles this efficiently.
    query = " OR ".join(f"cat:{c}" for c in cats)
    logger.info("arxiv query: %s", query)

    # Over-fetch ~5x because most won't match our keywords client-side.
    fetch_size = min(max_results * 5, 200)

    client = arxiv.Client(page_size=100, delay_seconds=3.0, num_retries=5)
    search = arxiv.Search(
        query=query,
        max_results=fetch_size,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    seen: set[str] = set()
    out: list[PaperMetadata] = []
    for result in client.results(search):
        if result.published < cutoff:
            break  # results are sorted desc, so we can stop
        meta = _result_to_metadata(result)
        if meta.arxiv_id in seen:
            continue
        seen.add(meta.arxiv_id)
        if not _matches_any_keyword(meta, keywords):
            continue
        out.append(meta)
        if len(out) >= max_results:
            break

    logger.info("arxiv: %d papers matched keywords (from category fetch)", len(out))
    return out


# --- LangChain @tool wrapper for use inside the ReAct loop ---


@tool
def search_arxiv(query: str, max_results: int = 10) -> str:
    """Search arXiv for recent AI/ML papers matching the query.

    Use this when you need to find papers on a specific topic. The query should
    be 1-5 keywords (e.g. "tool use agent", "ReAct scaffolding").
    Returns a newline-separated list of papers as 'arxiv_id | title | authors'.
    """
    keywords = [t.strip() for t in query.split() if t.strip()]
    papers = search_arxiv_recent(keywords=keywords, max_results=max_results)
    if not papers:
        return "No papers found."
    return "\n".join(f"{p.arxiv_id} | {p.title} | {', '.join(p.authors[:3])}" for p in papers)
