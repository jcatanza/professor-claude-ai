# ADR-0003: ProfessorState schema design

**Status:** Accepted
**Date:** 2026-05-06
**Deciders:** Joseph Catanzarite (with Claude as collaborator)

## Context

The LangGraph state object is the spine of the system — it flows between every
node and persists via the checkpointer. We need to choose what fields it carries.

Manning's book (ch 11.2.4) shows a minimal `AgentState` with just
`messages: Annotated[Sequence[BaseMessage], operator.add]`. The book's ch 12
summary recommends adding `current_agent` and `agent_history` for multi-agent
traceability.

Our use case has more structure than the book's travel assistant: we have
typed paper metadata, triage decisions, structured deep-read reports, and
You-Model context.

## Decision

We define `ProfessorState` as a `TypedDict(total=False)` extending the book's
pattern, with these fields:

- `run_id`, `run_date` — run identity
- `messages` (Annotated with `operator.add`), `current_agent`, `agent_history`
  — book conventions
- `candidate_papers`, `triage_decisions`, `deep_reads` — domain outputs
- `you_model_snapshot` — frozen view of user context for this run
- `daily_digest` — synthesis output
- `verification_flags`, `iteration_count` — anti-failure tracking

All non-message fields use replace semantics (default for TypedDict);
`messages` accumulates per the book's pattern.

Domain types (`PaperMetadata`, `TriageDecision`, `DeepReadReport`,
`ClaimWithProvenance`, `VerificationFlag`, `YouModelSnapshot`) are Pydantic
`BaseModel`s for validation and serialization.

## Rationale

1. **Pydantic models for domain types**: gives us validation, JSON
   serialization, and structured-output support from `langchain.with_structured_output()`.
2. **TypedDict for the state itself**: LangGraph's expected interface; allows
   fine-grained `Annotated` semantics for accumulating fields.
3. **`total=False`**: nodes don't need to populate every field on every call;
   they return only what they update.
4. **`ClaimWithProvenance` as first-class type**: bakes our anti-hallucination
   stance into the type system. Every claim must carry source attribution
   and a confidence label.
5. **`iteration_count`**: needed for the bounded-retry pattern from the book's
   ch 5.5 (relevance evaluator loops back, max iterations to avoid infinite loops).

## Consequences

**Easier:**
- Schema is documented and versioned
- Type errors caught by mypy in CI
- New nodes know exactly what fields are available

**Harder:**
- Schema migrations: as the system evolves, fields will be added/renamed.
  We need a versioning story for persisted state. v0.4 problem; for v0.1 we
  reset state on schema changes.

## Alternatives Considered

- **Single big dict with no types**: minimum ceremony, maximum chaos. Not
  maintainable past ~3 fields.
- **All Pydantic (no TypedDict)**: pydantic doesn't play as cleanly with
  LangGraph's `Annotated[..., operator.add]` pattern.
- **Separate state per agent**: more isolation but harder to reason about
  the full pipeline; the book uses a single shared state and that scales fine
  for our use case.

## References

- Manning AI Agents and Applications, ch 5 (typed state), ch 11.2.4 (AgentState),
  ch 12 summary (current_agent / agent_history recommendation)
- LangGraph state docs: https://langchain-ai.github.io/langgraph/concepts/low_level/#state
