# Decision Log

Append-only chronological record of decisions. Each entry: date, decision,
links to ADR if formal. Use this for "I know we discussed this — when?"
moments. ADRs go in `docs/adr/`.

---

## 2026-05-06 — Project kicked off

Decided on:
- Subfield for v0.1: **agents and harnesses**
- Output: both daily email AND GitHub repo entries
- Hosting: GitHub Actions (see [ADR-0002](adr/0002-github-actions-hosting.md))
- Stack: LangGraph + LangChain + ChromaDB + LiteLLM (see [ADR-0001](adr/0001-langgraph-stack.md))
- State schema: extending Manning's AgentState pattern (see [ADR-0003](adr/0003-state-schema.md))
- v0.1 graph topology: linear, not Supervisor (see [ADR-0004](adr/0004-linear-graph-vs-supervisor-v01.md))
- Compute path: API-only for now; GPU workstation remains on the table
- Manning book reading order: SLM first (informs v0.2 triage), Streamlit second (informs v0.3 interface)
- Hallucination policy: four mechanisms (provenance, calibrated confidence, verification pass, honest uncertainty); not "zero hallucination at all cost"
- Funding: apply to all three lab credit programs in parallel with build
- Engineering practices: tests, ADRs, CI, structured logging from day one (course-project compatible)
