# Professor.Claude.AI — Roadmap & Backlog

*Consolidated v0.1.1 → v0.2 action plan. Single source of truth replacing five prior chat-handoff documents.*

**Document version:** v1.0
**Date:** 2026-05-10
**Repository head at time of writing:** `acdc40f` on `origin/main`
**Author:** Claude (chat #6), edited and accepted by Joseph Catanzarite

---

## Status snapshot

**v0.1.1 is shipped and on `origin/main`.** Six commits constitute the version delta from the v0.1 spine:

| Commit  | Description                                                            | Chat |
|---------|------------------------------------------------------------------------|------|
| `acdc40f` | `fix(settings): expand default keyword list to match .env (runner parity)` | #5 |
| `7181a26` | `test: update tests for new triage threshold and synthesis signature`    | #5 |
| `49b038c` | `style: ruff format synthesis.py (fix CI lint)`                          | #5 |
| `73677dd` | `fix(ingestion): widen arxiv fetch window to days_back=2`                | #4 |
| `4a63624` | `fix(triage,synthesis): lower deep_read threshold, distinguish empty-digest cases, add titles` | #4 |
| `3795866` | `fix: handle empty-string secrets from CI env`                           | #3 |

CI is green through Run #11. Nightly Run #5 (manually triggered, 2026-05-09) ran end-to-end on `acdc40f` and produced an empty digest correctly — the keyword-parity fix was confirmed to land but the day was a Saturday with no arXiv announcements, so absence-of-content rather than failure.

**The first real-content test of the v0.1.1 pipeline is Nightly Run #6** — the scheduled run at 06:00 UTC Sunday May 10, ~4.5 hours after this document is being written. As of writing, that run has not yet fired. The most recent successful production digest is the original from chat #2: `docs/sample-digest-2026-05-07.md`.

**One cosmetic carryover:** the README still reads "Status: v0.1 (the spine)". This should be bumped to v0.1.1 in a small follow-up commit.

---

## How to read this document

The backlog uses a flat numbering scheme (items #1 through #33) that preserves traceability across five prior chat handoffs. **Items #1–#27 are sourced verbatim from prior handoff documents.** Items #28–#33 are derived in chat #6 from chat-#5's narrative; the chat-#5 handoff named that range but did not enumerate the items literally, so the list here is reconstructed and may not match what was originally intended. Numbering is preserved going forward — new items added in chat #7 should start at #34.

Each item is captured with: short title, one-paragraph description (including the *why*, not just the *what*), estimated effort, dependencies, and current status. Where an item maps to an existing or candidate ADR, the link is noted.

Effort estimates use the t-shirt scale: **S** = under an hour, **M** = an evening, **L** = a weekend, **XL** = multi-session architectural work. Status values: **todo** / **in-progress** / **done** / **deferred** / **blocked**.

---

## v0.1.1 — Cleanup and hardening

### Done in chats #2 through #5

These items are recorded for completeness; no further work needed.

- **#1** `pyproject.toml` missing `pypdf` — *not yet verified done; check Nightly #6 for `ModuleNotFoundError`*
- **#6** Synthesis "no deep reads tonight" misleading — done in `4a63624`. Three empty-cases distinguished.
- **#7** First commit and GitHub push — done in chat #2.
- **#13** Credential helper not yet caching the personal access token — resolved by subsequent pushes.
- **#18** Verify CI green on `33753e0` — done in chat #4. CI is now green through Run #11 / `acdc40f`.
- **#21** Digest needs paper titles — done in `4a63624`. Titles in deep-read headers and skim list.

### Bugs still open (must fix before v0.2)

- **#1** `pyproject.toml` missing `pypdf` — added manually via `uv pip install` during chat #1, but a fresh checkout would fail to deep-read because the dependency is not declared. Add `"pypdf>=5.0"` to `dependencies` in `pyproject.toml`. **S, no dependencies, todo.**
- **#2** `scripts/bootstrap.sh` missing `git init` — the bootstrap script tries to install pre-commit hooks before the git repository exists, so a fresh clone fails. Add `git init` (idempotent — re-running on an existing repo is safe) before the pre-commit step. **S, no dependencies, todo.**
- **#3** `.env.example` keyword line lacks quotes — the line `SUBFIELD_KEYWORDS=agent,...,tool use,...` breaks when sourced via `set -a && source .env` because of the embedded space in `tool use`. Wrap value in double quotes. **S, no dependencies, todo.**
- **#4** `.env.example` has `LANGSMITH_TRACING=true` by default — causes 403 errors flooding the log when no LangSmith key is set. Default to `false`; users opt in by changing the value. **S, no dependencies, todo.**
- **#5** CLI doesn't auto-load `.env` into environment — the Anthropic SDK reads `ANTHROPIC_API_KEY` from `os.environ`, not from the pydantic-settings object. Currently requires `set -a && source .env && set +a` before each manual run. Fix: in `cli.py`, before LangChain is imported, explicitly export `os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key`. **S, no dependencies, todo.**

### Quality-of-life improvements

- **#8** Promote `max_chars` truncation to settings — currently hardcoded `150_000` in `deep_read.py`. Move to `settings.py` as `MAX_DEEP_READ_CHARS=150000`, tunable from `.env`. **S, no dependencies, todo.**
- **#9** Promote `max_tokens_to_sample` to settings — currently hardcoded `16384` in `deep_read.py`. Move to `settings.py` as `DEEP_READ_MAX_TOKENS=16384`. **S, depends on #8 pattern, todo.**
- **#10** Promote `timeout` to settings — currently hardcoded `120.0` in `deep_read.py`. Move to `settings.py` as `DEEP_READ_TIMEOUT_SECS=120`. **S, depends on #8 pattern, todo.**
- **#11** Sample digest file has executable mode (`100755`) — markdown shouldn't be executable. Run `chmod 644 docs/sample-digest-2026-05-07.md && git add` and commit. Tiny lint smell. **S, no dependencies, todo.**
- **#12** GitHub repo "About" sidebar still empty — 2-minute browser task: add description and topic tags (`langgraph`, `claude`, `anthropic`, `arxiv`, `ai-agents`, `llm`, `research-tools`, `python`). Useful for discoverability. **S, no dependencies, todo.**
- **#22** Cache key strategy in `nightly.yml` is suspect — `key: professor-data-${{ github.run_id }}` is unique per run, will never hit on exact key, only via `restore-keys` prefix match. Probably intentional ("save unique, restore latest") but worth a code comment explaining the pattern. **S, no dependencies, todo.**
- **#23** Nightly workflow doesn't commit digests back to repo — currently digests live only as GitHub Actions artifacts (~90-day expiry). Should be committed to `docs/sample-digests/` for permanent reference. Add a step to the nightly workflow that copies new digests to `docs/sample-digests/` and pushes them. Watch out for permissions — the workflow's default `GITHUB_TOKEN` may need write access. **M, no dependencies, todo.**
- **#30** README still says "Status: v0.1 (the spine)" — should reflect v0.1.1. One-line change in `README.md`. **S, no dependencies, todo.**

### Optional / debatable

- **#24** GitHub Actions Node.js 20 deprecation — helper actions (`actions/checkout`, `actions/cache`, `astral-sh/setup-uv`, `actions/upload-artifact`) need version bumps before September 16, 2026 (hard deadline; soft deadline June 2, 2026). Not urgent yet. **S, no dependencies, todo.**
- **#25** Cron scheduling is suboptimal — current `0 6 * * *` UTC = 23:00 Pacific = 02:00 Eastern. Considered alternative `0 12 * * *` UTC = 05:00 Pacific = 08:00 Eastern, which would land Joseph's digest at start-of-business. With `days_back=2` already shipped, this is a UX choice not a bug fix. **S, no dependencies, todo (optional).**
- **#26** `interest_bonus` rarely fires — the check `interest.lower() in text` requires multi-word interest phrases like `"agent evaluation"` to appear verbatim. Real abstracts say "evaluating agents" or "agent benchmarking" instead. Consider per-token match in v0.2. The v0.1.1 threshold drop from 0.6 to 0.45 makes this less urgent. **S in v0.2, defer.**
- **#27** `react` keyword is doing too much (or too little) work — currently substring-matches via the `<= 6 chars` word-boundary regex. With word boundaries it correctly skips `reactor`/`reactive` but also skips `ReAct` (the prompting pattern). Worth an audit when keyword set is revisited. **Resolved in v0.2 by embedding-based triage; defer.**

### Deferred to v0.2 (originally listed for v0.1.1, better tackled later)

- **#14** Smart truncation Tier 1 (drop references/acks/related-work first) — defer until real digest output reveals which papers got short-changed. Premature otherwise.
- **#15** Map-reduce section reading Tier 2 — chunk paper into sections, summarize each with cheaper model (Haiku), feed concatenated summaries to Opus. Only implement if Tier 1 + 150K isn't enough.
- **#16** RLM-style recursive reading Tier 3 — already planned for v0.4 per Zhang/Khattab/Kraska 2025.
- **#17** Run pipeline a second night for taste-tuning — happened in chats #3 and #4. Ongoing, not a discrete item.

---

## v0.2 — Architectural improvements

This is where Professor.Claude.AI stops being a v0.1 spine and starts being a real research agent. Five major workstreams, in rough dependency order.

### Triage rewrite — embedding-based retrieval (the dominant v0.2 work)

This replaces keyword matching as the primary triage mechanism. The full proposal is captured as a draft ADR in the ADR section below. Effort: **XL**, multi-session work depending on the SLM-book reading first. **Status: proposed (ADR), todo (implementation).**

### Local SLM integration — `Item: separate from triage`

Originally planned (in chat #1's handoff) as the v0.2 triage solution: run a Gemma 2 9B model locally to classify candidate papers. The embedding-based proposal above supersedes this for *triage specifically*. However, a local SLM still has value for downstream tasks:

- **Sub-classification of triaged papers** by sub-topic (e.g. agents-vs-harnesses-vs-evaluation) for digest grouping
- **Cheap first-pass summarization** before the expensive Claude deep-read
- **Cost discipline** — a local model means infinite-budget experimentation on prompt engineering, free at any scale once the GPU is sunk

Pre-work: read Manning's *Domain-Specific Small Language Models* (Joseph's review queue, soft prerequisite). Effort: **L–XL** depending on scope. **Dependencies:** GPU access; SLM book read. **Status: proposed, deferred until embedding triage is in flight.**

### NLAH-lite — file-backed canonical workspace

Per *Natural-Language Agent Harnesses* (Pan et al., arXiv 2603.25723) read in chat #3. The paper's core contribution is externalizing harness logic — control flow, contracts, failure taxonomy — as portable text artifacts that an Intelligent Harness Runtime executes. NLAH-lite for Professor.Claude.AI means:

- Move agent prompts from Python string constants to YAML files with explicit input/output contracts
- Make the canonical workspace path-addressable (artifacts written to disk between agent steps, not just held in `ProfessorState`)
- Define an explicit failure taxonomy (`upstream_fetch_empty`, `pdf_parse_failed`, `api_timeout`, `validation_error`, ...) that downstream nodes can branch on instead of try/except sprawl
- Add a runtime charter document that defines retry/stop semantics

The benefit is testability and migrability. NLAH-lite agents can be rerun deterministically against frozen inputs; harness logic can be inspected and edited without touching Python code; failure modes become first-class objects rather than buried in stack traces. Effort: **L** for the YAML migration, **XL** if file-backed workspace is fully implemented. **Dependencies:** none hard, but Layer 4 memory work below benefits from this being done first. **ADR candidate. Status: proposed, todo.**

### Layer 4 memory — episodic, semantic, reflective

Per Park et al. 2023 (Smallville) and the modern A-MEM/Letta literature. Today's pipeline has two memory layers: short-term (LangGraph SqliteSaver checkpointer, within-run state) and long-term (ChromaDB + DuckDB for vectors and event log). v0.2 adds three more layers:

- **Episodic memory** — full record of every nightly run as a queryable event ("what did the digest contain on May 12?", "when did I first read Pan et al.?")
- **Semantic memory** — distilled facts about Joseph's interests, the field's vocabulary, and the relationship between papers (knowledge graph)
- **Reflective memory** — self-generated meta-summaries that the agent uses to recalibrate its taste model and triage thresholds over time

This is the architectural commitment Park 2023 actually represents — not a truncation method, which was a memory-mix-up early in chat #2 that was caught and corrected. Effort: **XL**. **Dependencies:** NLAH-lite is helpful but not strictly required; the schema for these memory layers belongs in an ADR. **ADR candidate. Status: proposed, todo.**

### Supervisor migration

Per ADR-0004. The current LangGraph wiring is a linear graph: ingestion → triage → deep-read → synthesis. v0.2 migrates to the Supervisor pattern from Manning's *AI Agents and Applications*, where a coordinator agent decides which sub-agents to invoke and in what order. The trigger is when **bounded retries** become necessary — e.g., re-triage when too few candidates pass the threshold, or re-deep-read with a lower cost ceiling when the first attempt fails. Linear graphs can't express conditional revisits cleanly; supervisor graphs can. Effort: **L**. **Dependencies:** none hard; concurrent with embedding triage. **Status: proposed (ADR-0004 already written), todo.**

---

## v0.3 and beyond — future work

### Streamlit review UI

A web interface where Joseph can browse digests, give thumbs-up/thumbs-down feedback that feeds the You-Model, and trigger manual deep-reads on papers the triage missed. Deferred until Manning's *Build Python Web Apps with Streamlit* is read. Effort: **L**. **Dependencies:** Streamlit book; stable v0.2 backend.

### RLM-style recursive reading

Per Zhang/Khattab/Kraska 2025. Recursive Language Models read a long document by spawning sub-readers for each section, each of which can spawn further sub-readers, and propagate structured summaries back up. Replaces the current "truncate at 150K chars" approach with a principled recursive descent. Effort: **XL**. **Dependencies:** episodic memory layer (so sub-reads are addressable artifacts).

### Multi-source ingestion

Currently ingests arXiv only. Adding sources broadens coverage:
- **alphaXiv** — community annotations and discussion on arXiv papers
- **HuggingFace Daily Papers** — curated subset with social signal
- **OpenReview** — pre-publication peer review
- **Semantic Scholar** — citation graph for finding follow-up work

Each source is its own ingestion adapter; the ingestion-agent interface should be widened in v0.2 (NLAH-lite contract work) so adding sources doesn't require triage/deep-read changes. Effort: **M per source.** **Dependencies:** NLAH-lite contracts.

### Email digest delivery

Currently digests print to terminal and (after item #23) commit to repo. Email delivery would mean Joseph reads the digest in his inbox during morning coffee instead of `cd ~/dev/professor-claude-ai && cat data/digests/...`. Effort: **M.** **Dependencies:** stable digest format; transactional-email service (SendGrid, Mailgun, or AWS SES — pick one in an ADR).

---

## Cross-cutting concerns

These are not single backlog items — they're recurring failure modes or systemic constraints that need a structural answer rather than per-occurrence patches.

### Pre-commit and CI environment parity (recurring class)

Three confirmed instances of the same bug class:

1. **Chat #3** — pre-commit's mypy ran with a stripped-down environment that treated `langgraph`, `langchain-core`, and other stack imports as `Any`. CI's mypy installed everything from `pyproject.toml` and saw real types. Pre-commit passed locally; CI failed. Resolved by mirroring CI's installed packages into pre-commit's `additional_dependencies`.
2. **Chat #5** — pre-commit's ruff (pinned to `v0.5.7`) and CI's ruff (latest from `pyproject.toml`) disagreed about whether a long f-string should be on one line or split. Pre-commit passed; CI failed.
3. **Chat #5** — `settings.py`'s default keyword list (5 keywords) and `.env`'s active keyword list (8 keywords) drifted. The GitHub runner uses the default because `.env` is gitignored. Pre-commit can't catch this because it has no concept of "production environment vs dev environment."

The root cause is the same in all three: **pre-commit and CI run in isolated environments, and pre-commit's environment doesn't reflect production reality.** Per-occurrence patches (instances 1 and 2 fixed locally) don't address the class.

Structural fix candidates (ADR territory):

- **Pin pre-commit and CI to the exact same tool versions** via a single source of truth (e.g., a `requirements-dev.txt` referenced by both)
- **Add a "smoke-test in CI environment" hook** — a CI job that runs the full pipeline against frozen test data, catching configuration drift the way item 3 would have surfaced
- **Make `.env.example` the source of truth** and have `settings.py` defaults match `.env.example` literally, with a CI check that fails if the two diverge

This is **ADR candidate territory** and should be written before the next refactor. **Status: ADR not yet written.**

### Configuration management — settings.py vs .env

A specific instance of the parity problem above, but worth its own treatment because configuration drift will be a recurring issue as the project gains parameters. Today's pattern:

- `settings.py` defines defaults for every parameter using pydantic-settings
- `.env` (gitignored) overrides defaults for the developer's local environment
- `.env.example` (committed) shows the parameters but contains placeholders
- The GitHub Actions runner has no `.env`, so it uses `settings.py` defaults

This pattern works as long as `.env` only contains *overrides for the developer's local convenience*. It breaks when `.env` is treated as the source of truth (as the keyword list was). The right answer probably involves a hierarchy:

- **Secrets** (API keys) — never in code, always in environment, never default-able. Status today: handled correctly.
- **Production-correct values** — committed in code (`settings.py`). The runner uses these. Status today: keyword list is now correct here after `acdc40f`.
- **Developer convenience overrides** — `.env`, gitignored, optional. Status today: works as intended for local dev.

Worth an ADR before more parameters get promoted to settings (items #8–#10 will add three). **ADR candidate. Status: not yet written.**

### Cost discipline

Self-funded budget is $25/month. Current spend pattern is dominated by deep-read API calls (~$0.10–$0.20 per paper at 16K tokens output). Two papers per night × 30 nights = $6–$12/month if every paper succeeds, less if API failures abort some.

Tactical guards already in place:
- `MAX_DEEP_READS_PER_RUN=2` cap (originally `1`, considered `3`)
- 150K-character truncation on input
- Triage threshold prevents runaway promotion

What's missing:
- **Budget tracking** — there's no recorded cost per run; we infer from Anthropic console
- **Soft circuit breaker** — if cumulative monthly spend exceeds a threshold, the nightly should switch to "skim only" mode rather than deep-reading
- **Local-model fallback** — once a local SLM is in place (v0.2), it can do degraded-mode summarization for free when budget is exhausted

This couples to the local SLM integration above and the embedding-triage proposal (which inverts the cost curve at scale by making local embedding free). **Status: tactical guards in place; structural cost-discipline ADR candidate, not yet written.**

---

## Architectural Decision Records

### Existing ADRs (in `docs/adr/`)

The exact list is in the repo at `docs/adr/`. From references in handoffs:

- **ADR-0003** — State schema (the `ProfessorState` TypedDict)
- **ADR-0004** — Linear graph today, supervisor pattern in v0.2
- (Others exist; refresh from repo before using this list as a reference.)

### ADR candidates from this roadmap (not yet written)

| ID  | Title                                       | Trigger                              |
|-----|---------------------------------------------|--------------------------------------|
| TBD | Embedding-based triage                      | Before v0.2 triage rewrite starts    |
| TBD | NLAH-lite adoption                          | Before YAML prompt migration starts  |
| TBD | Layer 4 memory schema                       | Before episodic store implementation |
| TBD | Pre-commit / CI environment parity strategy | Before next refactor                 |
| TBD | Configuration management hierarchy          | Before items #8–#10 ship             |
| TBD | Cost-discipline circuit breakers            | When monthly spend approaches ceiling |
| TBD | Email delivery transactional service choice | Before email-delivery work starts    |

### Draft ADR — Embedding-based triage

This is the major architectural decision proposed in chat #5. Drafted here in roadmap form; should be promoted to a real ADR document (`docs/adr/00NN-embedding-triage.md`) before implementation begins.

**Status:** proposed.

**Context.** Today's triage uses keyword matching plus a hand-tuned scoring function. Three problems compound:

1. **High false-positive rate.** "Agent" matches agriculture papers and chemistry agents alongside LLM agent papers. The substring approach can't discriminate by topic, only by vocabulary.
2. **Doesn't generalize.** Adding a sub-field (say, "interpretability") requires hand-curating a new keyword list, then tuning thresholds against expected false-positive and false-negative rates.
3. **Manual tuning is fragile.** Each threshold change ripples — the chat-#4 threshold drop from 0.6 to 0.45 was empirically derived from a single run's score distribution and is not robust to changes in keyword count, paper volume, or arXiv's category mix over time.

**Decision (proposed).** Replace keyword-based triage with embedding-based retrieval:

1. Maintain a per-sub-field **canonical paper list** — 5–10 anchor papers per sub-field, manually curated, that exemplify what Joseph cares about
2. Encode each canonical paper into a high-dimensional embedding vector using a domain-appropriate model (Specter2 is the leading candidate for academic papers; sentence-transformers is the simpler fallback)
3. Each night, encode every candidate arXiv paper into the same embedding space
4. For each sub-field, compute cosine similarity between every candidate and every anchor
5. Retrieve the **top-K most similar candidates per sub-field** (proposed K = 20), not papers above an absolute similarity threshold

Top-K is the critical sub-decision. Absolute thresholds suffer from drift — what counts as "highly similar" changes as the corpus changes. Top-K forces capacity-thinking ("we have budget for 20 deep-skim candidates per sub-field") instead of similarity-thinking ("how similar is similar enough?"). Top-K is also the standard primitive in production recommender systems for exactly these reasons.

**Why this is better than the originally-planned v0.2 SLM classifier (or how they coexist).**

The original v0.2 plan was a local Gemma 2 9B classifier doing triage. Embedding similarity is a different and arguably better approach for *triage specifically*:

- Embeddings exploit the geometric structure of pretrained representations directly; classification adds a learned mapping on top that needs labels
- Embeddings generalize without retraining; adding a sub-field is "drop in 5 anchor papers" rather than "label a few hundred examples and retrain"
- Embeddings of arXiv papers are reusable across nights — papers don't change, so dot-products are eternal once computed; the existing `data/chroma/` ChromaDB store is already provisioned for this
- The cost story scales differently — see below

The SLM still has value for downstream tasks: sub-classification of triaged papers, cheap first-pass summarization, free experimentation. Both paths can coexist; embedding triage doesn't retire the SLM plan, it focuses it.

**Open questions (to resolve before promoting this draft to a real ADR).**

- Embedding model choice: Specter2 (purpose-built for academic papers) vs sentence-transformers (general-purpose) vs an Anthropic embedding endpoint (when available). Specter2 is leading; needs validation against a held-out set of papers Joseph has flagged as relevant.
- Where ChromaDB fits in the storage layout: probably as the anchor + candidate vector store; needs an index strategy (HNSW parameters, distance metric).
- Top-K value: starting estimate K=20 per sub-field, but actual K depends on per-sub-field corpus size and downstream cost (deep-skim is cheaper than deep-read but not free).
- Cold-start novelty fallback: a genuinely new paper may be far from every anchor, by design. Need a "sparse anchor zone" detector that surfaces papers in low-density regions of the embedding space — these may be the most interesting ones.
- Polysemy: paper-level embeddings collapse multi-topic papers into a single vector. May need section-level embeddings (abstract vs methods vs conclusion separately) for cross-disciplinary papers.

**Pre-work needed.**

- Finish reading Manning's *Domain-Specific Small Language Models* — informs the model choice and gives a vocabulary for evaluation
- Curate the first canonical paper list for the agents-and-harnesses sub-field (5–10 papers; Joseph already has candidates from his current reading queue)
- Spike: encode 100 recent arXiv papers, hand-rate top-K against Joseph's intuition, check whether K=20 captures everything that should be captured

**Joseph's "hold this thought" — local embeddings invert the cost curve at scale.**

API-based embedding (e.g., OpenAI's `text-embedding-3-large`) costs roughly $0.0001 per paper at typical lengths. Trivial at 100 papers/night. Prohibitive at 100,000 papers/night.

Local embedding (Specter2 or sentence-transformers running on a single GPU) inverts this. After the one-time cost of GPU access, encoding is free at any scale. Whatever path Professor.Claude.AI takes — staying small and personal, or scaling to multi-user or multi-domain — the local-embedding option becomes increasingly attractive as scale increases. This is worth surfacing again when v0.2 is being designed in earnest, especially if the project ever pivots toward serving more than one user.

**What gets discarded from v0.1.** Nothing, actually. Keyword matching becomes a stage-1 cheap pre-filter that runs *before* embedding similarity, narrowing the candidate pool the embedding stage has to handle. So the v0.1 keyword work is repurposed, not retired. This also addresses item #27 (the `react` keyword regex ambiguity) — it stops mattering once embeddings are doing the discrimination.

---

## Reference material

### Papers

- **Pan et al. 2026** — *Natural-Language Agent Harnesses* (arXiv 2603.25723). Source of NLAH-lite. Read in chat #3.
- **Lin et al. 2026** — *Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses* (arXiv 2604.25850). v0.3+ reference; not near-term.
- **Park et al. 2023** — *Generative Agents* (Smallville). Source of the Episodic / Semantic / Reflective memory model.
- **Zhang, Khattab, Kraska 2025** — Recursive Language Models. Source of the RLM-style deep-read approach for v0.4.
- **Infante 2026** — *AI Agents and Applications* (Manning). LangGraph patterns, supervisor architecture. Already informs current code.
- **Manning's *Domain-Specific Small Language Models*** (forthcoming) — soft prerequisite for v0.2 triage / SLM work.
- **Manning's *Build Python Web Apps with Streamlit*** (forthcoming) — prerequisite for v0.3 Streamlit UI.

### External libraries / tools likely to enter v0.2

- **Specter2** (or sentence-transformers as fallback) — embeddings
- **ChromaDB** — already provisioned, will host anchor and candidate vectors
- **LiteLLM** — model-agnostic interface (defer until multi-provider becomes a real need)
- **Streamlit** — v0.3 UI
- **A YAML schema validator** (Pydantic, jsonschema) — for NLAH-lite prompt contracts

### Connections to coursework

- **Modern Software Concepts (starts May 18).** Public-repo requirement aligns with the project. Topics likely to overlap: testing strategy, CI/CD discipline, configuration management, ADR-style documentation, dependency management.
- **LLMs Theory and Practice.** Embedding-triage proposal is a direct application; can serve as a course-project case study.
- **Generative AI.** The deep-read agent's prompt engineering (especially the cutoff-awareness patch from chat #2) is a course-relevant artifact.

### Working-smarter conventions accumulated across chats

These belong here as a quick reference; the original full discussions are in the chat handoffs.

- Filenames carry version (`<name>_v<X.Y>.md`)
- Code patches use the download-and-cp pattern; never paste-into-nano or shell heredocs
- Always call `present_files` for files Joseph needs
- Idempotent patches with `assert old in text; assert new not in text` guards
- Pre-commit dependency parity with CI is mandatory (see cross-cutting concern above)
- Project-knowledge files go stale; refresh from real source (raw URL or local paste) before patching
- Use `git --no-pager` for diff/log/show in chat-driven workflows
- `cat -A` reveals whitespace differences `cat` hides
- Don't ask Joseph to paste multi-line shell content; multi-line input is a recurring paste-mangling trap
- Verify manual file moves with `ls -la` before issuing further commands
- Expand acronyms on first use, every chat (CI = Continuous Integration; ADR = Architecture Decision Record; SLM = Small Language Model; NLAH = Natural-Language Agent Harness; PR = pull request; etc.)
- The "All workflows" page on GitHub Actions renders unreliably for unauthenticated viewers; use the per-workflow page (`/actions/workflows/<name>.yml`) for accurate state

---

## What this document is and isn't

**Is:** the single source of truth for v0.1.1 backlog items, v0.2 architectural plans, and v0.3+ deferred work. Replaces five chat-handoff documents as the place to look up "what was that decision again?" or "did we ever fix item #6?"

**Isn't:** a sprint plan, a release schedule, or a committed roadmap. Items are listed with effort and dependencies; what gets worked on next is a separate decision made by Joseph each session, weighed against current priorities (Modern Software Concepts coursework starting May 18, budget, energy).

**Maintenance:** when an item is completed, mark it done with the commit hash. When new items emerge, add them with the next available number (start at #34). When an ADR candidate becomes a written ADR, replace the candidate row with the ADR number and link.

---
---
## New items from chat #8 and #9

- **#44 — Rolling candidate pool.** Carry near-miss papers from prior nights into the current night's pool. Likely obsoleted by v0.2 embedding-based top-K retrieval; worth implementing as a stopgap if v0.2 slips past mid-July. Design questions: window length; re-triage vs. cached scores; double-deep-read prevention via persistent state; digest format ("carried from prior night" marking). **M, depends on persistent state layer, deferred.**

- **#45 — Pause-mode for nightly cron during high-coursework periods.** Options: (a) manual `gh workflow disable nightly` / `gh workflow enable nightly` with documented runbook — implemented in chat #9; (b) `PAUSED=true` env var that defaults workflow to early-exit; (c) calendar-driven via `config/pause.yml`. Option (a) is zero-code and in use now. **S, no dependencies, todo.**

- **#46 — GitHub Actions UI inconsistency investigation.** Unauthenticated All-workflows page renders unreliably; routed around via per-workflow URL convention. Investigate whether GitHub has a documented limitation; file a bug if not; retire workaround if upstream-fixed. **S, no dependencies, low priority.**
*End of roadmap.*
