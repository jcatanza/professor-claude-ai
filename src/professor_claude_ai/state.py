"""LangGraph state schema for Professor.Claude.AI.

This is the spine of the whole system. Every node receives this state and
returns updates that get merged in.

Design notes:
- Extends the AgentState pattern from Manning AI Agents and Applications ch 11.2.4
  (messages: Annotated[..., operator.add])
- Adds current_agent and agent_history per the book's ch 12 summary recommendation
  for multi-agent traceability
- Adds iteration_count for bounded retries (ch 5.5 pattern: relevance evaluator
  loops back to query generation, capped to avoid infinite loops)
- Adds Professor-specific fields for paper triage, deep-read outputs, You-Model
  context, and verification flags

See docs/adr/0003-state-schema.md for full justification.
"""

from __future__ import annotations

import operator
from collections.abc import Sequence
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

# ---------- Domain types ----------


class PaperMetadata(BaseModel):
    """Lightweight metadata for a candidate paper (pre-triage)."""

    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    primary_category: str
    submitted_date: str  # ISO date
    pdf_url: str
    abs_url: str


class TriageDecision(BaseModel):
    """Outcome of the triage stage for a single paper."""

    arxiv_id: str
    decision: str  # "skip" | "skim" | "deep_read"
    score: float = Field(ge=0.0, le=1.0)
    reason: str
    matched_keywords: list[str] = Field(default_factory=list)


class ClaimWithProvenance(BaseModel):
    """A single claim from a deep-read, with traceback to the source.

    This is the core anti-hallucination unit: every assertion in a deep-read
    output must be expressible as one of these, with confidence and provenance.
    """

    claim: str
    source_section: str  # e.g. "Section 4.2", "Table 3", "Appendix B"
    source_quote: str | None = None  # short verbatim, paraphrase preferred
    confidence: str  # "high" | "medium" | "low"
    is_verified: bool = False  # True after verification pass
    verification_note: str | None = None


class DeepReadReport(BaseModel):
    """Structured output of the deep-read agent for a single paper.

    Mirrors the 8-point template from the design plan §4.
    """

    arxiv_id: str
    background: str
    core_innovation: str
    methodology_strengths: list[str]
    methodology_weaknesses: list[str]
    results_summary: str
    relevance_to_user: str  # framed against You-Model
    connections: list[str]  # links to other papers in memory
    key_equations_or_diagrams: list[str]
    claims: list[ClaimWithProvenance]
    overall_confidence: str  # "high" | "medium" | "low"


class VerificationFlag(BaseModel):
    """A discrepancy found during the verification pass."""

    arxiv_id: str
    claim_index: int
    flag_type: str  # "numerical_mismatch" | "missing_source" | "ambiguous_attribution"
    description: str


class YouModelSnapshot(BaseModel):
    """Read-only snapshot of the You-Model passed into a run.

    The full You-Model is mutable across runs; this is a frozen view for one run.
    v0.1: minimal (declared interests + current courses + reading list).
    v0.3: full knowledge state, engagement history, spaced-repetition flags.
    """

    declared_interests: list[str]
    current_courses: list[str]
    current_reading: list[str]
    recent_thumbs_up_arxiv_ids: list[str] = Field(default_factory=list)
    recent_thumbs_down_arxiv_ids: list[str] = Field(default_factory=list)


# ---------- The graph state ----------


class ProfessorState(TypedDict, total=False):
    """LangGraph state for one nightly run of Professor.Claude.AI.

    Per Manning ch 11.2.4: messages uses operator.add so each node's returned
    messages get appended rather than replacing. Other fields use default
    (replace) semantics.
    """

    # --- Run identity ---
    run_id: str  # UUID
    run_date: str  # ISO date

    # --- Conversation / orchestration (Manning ch 11.2.4 + ch 12 summary) ---
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_agent: str | None
    agent_history: list[str]

    # --- Ingestion outputs ---
    candidate_papers: list[PaperMetadata]

    # --- Triage outputs ---
    triage_decisions: list[TriageDecision]

    # --- Deep-read outputs (with provenance) ---
    deep_reads: list[DeepReadReport]

    # --- You-Model context (read by triage and deep-read) ---
    you_model_snapshot: YouModelSnapshot

    # --- Synthesis output ---
    daily_digest: str | None

    # --- Anti-failure tracking ---
    verification_flags: list[VerificationFlag]
    iteration_count: int  # bounded retries (Manning ch 5.5 pattern)
