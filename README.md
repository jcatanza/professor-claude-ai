# Professor.Claude.AI

[![CI](https://github.com/jcatanza/professor-claude-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/jcatanza/professor-claude-ai/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Built with LangGraph](https://img.shields.io/badge/built_with-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)

> An autonomous self-teaching AI research agent. Runs nightly to ingest, triage, deeply read, and synthesize new developments in AI research — keeping its human collaborator at the frontier with roughly an hour of focused review per day.

**Status:** v0.1 (the spine). End-to-end working pipeline, narrow but real. See [sample digest](docs/sample-digest-2026-05-07.md) from the first successful production run.

## What it does

1. **Ingests** new arXiv papers in the agents-and-harnesses subfield each night
2. **Triages** them — most are skipped, a few are skimmed, the best 1–2 earn deep attention
3. **Deep-reads** those papers via Claude, producing structured analyses with provenance
4. **Writes** to a persistent memory layer (short-term checkpoints + long-term semantic store)
5. **Emits** a daily digest — both as email and a markdown commit to a private GitHub repo

Architecture decisions are tracked in [`docs/adr/`](docs/adr/) and the project [decision log](docs/decision-log.md). The full v0.3 design plan is maintained in private project notes and will be sanitized for public release in a future revision.

## Architecture at a glance

Built on **LangGraph** with the **Supervisor pattern** from Manning's *AI Agents and Applications* (Roberto Infante, 2026).

```
Nightly Coordinator (Supervisor)
    ├── Ingestion Agent   (arXiv, RSS, HF Daily)
    ├── Triage Agent      (keyword filter + you-model + taste model)
    ├── Deep-Read Agent   (ReAct + ToolNode, structured analysis)
    └── Synthesis Agent   (digest formatting, email + repo commit)
```

Persistent state is layered:
- **Short-term:** LangGraph `SqliteSaver` checkpointer (within-run state)
- **Long-term:** ChromaDB (vector RAG) + DuckDB (episodic event log) + a four-layer Smallville-inspired memory model on top (v0.3+)

## Quickstart

```bash
# Clone and enter
git clone <your-fork-url> professor-claude-ai
cd professor-claude-ai

# Set up environment (uv recommended; pip works too)
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Configure secrets
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY at minimum

# Run a single nightly cycle locally (won't actually email yet — dry run)
professor-run --dry-run

# Run for real
professor-run
```

## Project layout

```
src/professor_claude_ai/
  agents/        Supervisor + sub-agents (ingestion, triage, deep-read, synthesis)
  memory/        SqliteSaver, ChromaDB, DuckDB wrappers + the You-Model
  tools/         ReAct tool functions (search_arxiv, fetch_paper, verify_claim, ...)
  config/        Pydantic settings, prompt templates
  state.py       The ProfessorState TypedDict (see docs/adr/0003-state-schema.md)
  graph.py       The LangGraph wiring
  cli.py         Entry points (professor, professor-run)

tests/
  unit/          Per-module unit tests
  integration/   End-to-end run with mocked external calls

docs/
  design-plan.md   Living design document
  adr/             Architecture Decision Records
```

## Testing

```bash
# All tests
pytest

# Just unit tests (fast)
pytest tests/unit

# Integration tests (slow, hits mocked external services)
pytest tests/integration -m integration

# Type-check
mypy src

# Lint and format
ruff check .
ruff format .
```

## Operational

- **Schedule:** Nightly via GitHub Actions (`.github/workflows/nightly.yml`)
- **Observability:** [LangSmith](https://smith.langchain.com) tracing (set `LANGSMITH_TRACING=true`)
- **Failure recovery:** State checkpoints written after every node — failed runs resume from last checkpoint on next invocation
- **Cost monitoring:** Daily token usage logged; weekly summary in digest

## Anti-failure mechanisms

The design explicitly guards against five failure modes (see `docs/design-plan.md` §2):

1. **Information overload** — hard cap on deep-reads per run; tunable triage thresholds
2. **Hallucinated claims** — provenance everywhere, calibrated confidence, verification pass on numerical claims, honest uncertainty
3. **Echo chamber** — periodic "outside view" sweeps; topic diversity metrics
4. **Stale interests** — field-shift detector; quarterly taste-model recalibration
5. **Over-engineered & unused** — spine-first build; weekly check that you actually read the digests

## License

MIT — see [LICENSE](LICENSE).

The Manning book *AI Agents and Applications* (Roberto Infante, 2026) is referenced extensively in design documents. Code patterns are adapted under fair use for educational/personal-research purposes; no verbatim source from the book is reproduced.
