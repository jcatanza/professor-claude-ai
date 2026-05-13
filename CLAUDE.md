# Professor.Claude.AI — Agent Context

## What this project is
A personal research-digest agent that fetches arXiv papers nightly, triages them
against Joseph's research interests, deep-reads the top candidates, and synthesizes
a daily digest. Built on LangGraph (graph-based agent orchestration framework).

## Repo layout
- `src/` — core pipeline code (fetch, triage, deep-read, synthesis)
- `docs/` — roadmap, ADRs (Architecture Decision Records), design docs
- `docs/adr/` — architectural decisions (read these before suggesting changes)
- `docs/references/` — local reference files, gitignored
- `.github/workflows/` — nightly CI (Continuous Integration) cron, currently disabled

## Current state (as of May 12 2026)
- `origin/main` head: `4710d21`
- Nightly workflow manually disabled until post-June 11 2026
- Active roadmap: `docs/roadmap_v0_1_1_to_v0_2.md`

## Conventions
- Python, Pythonic style for simple cases, explicit for complex logic
- `git --no-pager` for all git commands
- Pre-commit hooks enforce ruff, mypy, whitespace — run before committing
- All architectural decisions go in `docs/adr/` before implementation
- Single source of truth for backlog: `docs/roadmap_v0_1_1_to_v0_2.md`

## Do not touch without discussion
- LangGraph state schema (`docs/adr/0003-state-schema.md`)
- Anything tagged v0.2 or later in the roadmap — deferred
