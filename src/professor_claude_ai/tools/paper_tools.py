"""Paper fetching and text extraction tools.

v0.1: simple PDF fetch + text extraction. Good enough for most papers.
v0.4: migrate to RLM-style recursive reading (Zhang/Khattab/Kraska 2025) so we
don't suffer context rot on long papers.
"""

from __future__ import annotations

import logging
from io import BytesIO

import httpx
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


def fetch_paper_text(pdf_url: str) -> str:
    """Download a paper PDF and extract its text.

    Returns extracted text, or empty string on failure.
    """
    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(pdf_url)
            response.raise_for_status()
            pdf_bytes = response.content
    except httpx.HTTPError as e:
        logger.warning("Failed to fetch %s: %s", pdf_url, e)
        return ""

    # Use pypdf for text extraction. Lighter than pdfplumber for our needs.
    try:
        from pypdf import PdfReader  # local import keeps top-level fast
    except ImportError:
        logger.error("pypdf not installed. Add it to dependencies.")
        return ""

    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        chunks = [page.extract_text() for page in reader.pages]
        return "\n\n".join(c for c in chunks if c)
    except Exception as e:  # — pypdf raises a variety of types
        logger.warning("Failed to parse PDF from %s: %s", pdf_url, e)
        return ""


@tool  # type: ignore[misc]
def fetch_paper(arxiv_id: str) -> str:
    """Fetch the full text of an arXiv paper given its ID.

    Use this when you need to deep-read a paper. The arxiv_id is the bare ID
    like '2401.12345', without the 'arXiv:' prefix or version suffix.
    Returns the full text, or an error message starting with 'ERROR:'.
    """
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
    text = fetch_paper_text(pdf_url)
    if not text:
        return f"ERROR: failed to fetch or parse {arxiv_id}"
    return text
