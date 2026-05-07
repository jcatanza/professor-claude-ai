# ADR-0004: Linear StateGraph in v0.1; migrate to Supervisor in v0.2

**Status:** Accepted
**Date:** 2026-05-06
**Deciders:** Joseph Catanzarite (with Claude as collaborator)

## Context

The design plan calls for the **Supervisor pattern** (Manning ch 12.3) as the
target orchestration approach. The Supervisor coordinates multiple sub-agents
and is well-suited to our multi-step nightly run.

However, v0.1's flow is fully deterministic: `ingestion → triage → deep_read
→ synthesis`. There is no branching, no need for an LLM-based dispatcher, no
re-entry. A Supervisor here would be all overhead and no payoff.

## Decision

For **v0.1**, we use a **simple linear `StateGraph`** with explicit
`add_edge` calls.

In **v0.2**, when we add bounded retries (re-triage if zero deep-read
candidates pass) and parallel ingestion across multiple sources, we migrate to
the **Supervisor pattern** per the book.

## Rationale

1. **Don't pay for what you don't use**: a Supervisor adds an LLM call per
   dispatch. v0.1's flow doesn't need dispatch.
2. **Simpler to debug**: a linear graph is grep-able; a Supervisor's
   decisions live in LLM completions.
3. **Cheaper to test**: linear graphs can be exercised end-to-end without
   any LLM calls (everything stub-able).
4. **Migration is mechanical**: when we go to Supervisor, the sub-agent
   functions don't change — only the orchestration layer does.

## Consequences

**Easier:**
- v0.1 lands faster and is easier to verify
- Lower cost per run

**Harder:**
- We'll do a small refactor in v0.2 (mechanical, well-bounded)
- Doesn't yet exercise the patterns from the book's most relevant chapter
  (ch 12); that comes in v0.2

## Alternatives Considered

- **Supervisor from day one**: discussed; rejected because the orchestration
  decisions are trivial in v0.1 and adding the layer obscures rather than
  clarifies.
- **No graph at all (just sequential function calls)**: gives up free
  checkpointing. Not worth the saving.

## References

- Manning AI Agents and Applications, ch 12.3 (Supervisor pattern)
- Migration plan: design-plan §5 (v0.2 includes "first feedback loop", which
  requires conditional re-routing — that's when Supervisor earns its place)
