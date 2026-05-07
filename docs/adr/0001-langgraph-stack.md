# ADR-0001: Use LangGraph + LangChain as the agent framework

**Status:** Accepted
**Date:** 2026-05-06
**Deciders:** Joseph Catanzarite (with Claude as collaborator)

## Context

Professor.Claude.AI requires an agent framework for orchestrating ingestion,
triage, deep-read, and synthesis nodes with shared state. The framework needs to
support: typed state, conditional branching, multi-agent coordination, persistent
checkpointing, and observability. We also have Manning's *AI Agents and
Applications* (Roberto Infante, 2026) in hand, which uses LangGraph 1.0 +
LangChain 1.0 throughout.

## Decision

We use **LangGraph 1.0 + LangChain 1.0** as the agent framework, following the
patterns from the Manning book.

## Rationale

1. **The book is current**: published 2026, uses LangGraph 1.0 / LangChain 1.0
   (the post-major-rewrite versions). Its patterns are not stale.
2. **Massive head start**: chapters 5, 11, 12, 14 cover the exact patterns we
   need (StateGraph, ReAct + ToolNode, Supervisor, SqliteSaver checkpointer).
3. **Free observability via LangSmith**: tracing comes built-in, which solves
   our provenance / audit-trail requirement nearly for free.
4. **Persistent checkpointing**: SqliteSaver gives us state rehydration on
   failure for free — important for unattended overnight runs.
5. **Manning book review synergy**: I'll be reviewing two Manning books that
   indirectly relate; using their stack for a working example helps both reviews.

## Consequences

**Easier:**
- v0.1 spine is mostly wiring up patterns from the book, not invention
- Migration to multi-agent (Supervisor) is well-supported
- LangSmith traces give us provenance audit trail nearly for free

**Harder:**
- LangChain has historical churn — we pin minor versions and bump deliberately
- Some non-trivial features (e.g. RLM-style recursive deep reads) will need
  custom work that doesn't fit cleanly into LangGraph idioms

## Alternatives Considered

- **CrewAI**: simpler multi-agent but less mature checkpointing; would need
  to build state-rehydration ourselves
- **Microsoft AutoGen**: powerful but steeper learning curve; less aligned
  with the Manning book's patterns
- **Roll-our-own with raw OpenAI/Anthropic SDK**: more control, but we'd
  reinvent state management, retries, and observability. Costs more dev time
  than the framework abstraction does.

## References

- Manning AI Agents and Applications, ch 5 (LangGraph basics), ch 11 (tool agents),
  ch 12 (multi-agent), ch 14 (production memory + guardrails)
- LangGraph docs: https://langchain-ai.github.io/langgraph/
