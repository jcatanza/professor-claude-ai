# Sample Digest — 2026-05-07

This is the actual output from the first successful production run of Professor.Claude.AI v0.1, captured for portfolio purposes.

## Run context

- **Date:** 2026-05-07
- **Subfield:** Agents and harnesses (`cs.AI`, `cs.LG`, `cs.CL` filtered by keywords)
- **Pipeline:** arXiv ingestion -> keyword/score triage -> Claude Opus 4.7 deep-read -> markdown synthesis
- **Candidates surveyed:** 22
- **Deep-reads:** 2
- **Skims:** 20
- **Failures:** 0

The deep-read agent uses structured output (Pydantic schema) to produce reports with provenance-tagged claims, calibrated confidence, and explicit links to the user's declared interests and current courses.

## Note on epistemic stance

An early version of the deep-read prompt did not tell the agent its training cutoff. As a result, the agent sometimes flagged post-cutoff papers as "AI-generated" when it didn't recognize cited model names like "GPT-5.4" or "Gemini-3-Flash-Preview". The system prompt was patched mid-session to acknowledge the cutoff explicitly and reserve fabrication flags for verifiable internal inconsistencies (cost arithmetic, self-contradictions, citations dated after the paper's own publication). The digest below is from the post-patch run and shows the corrected behavior.

---

# Professor.Claude.AI — Daily Digest, 2026-05-07

Surveyed 22 candidate papers. Deep-reads: 2. Skims: 20. Skipped: 0.

---

## Deep reads

### 2605.05191

**Background.** Long-horizon search agents built on the ReAct paradigm (Yao et al., 2023) accumulate reasoning traces, tool calls, and observations into an ever-growing context window. As trajectories extend over hundreds of steps, this append-only design degrades signal-to-noise ratio, raises inference cost, and eventually exceeds context limits. Prior remedies fall into four families: (1) sliding-window truncation (e.g., MiroThinker's keep-last-k), which is importance-agnostic; (2) discard-all/restart on threshold (DeepSeek-V3.2, GLM-4.7), which breaks reasoning continuity; (3) periodic summarization with fixed granularity (MEM1, MemAgent), which accumulates abstraction errors; and (4) proactive curation (AgentFold, ARC), which gives the agent some control but lacks fine-grained or retroactive operations.

**Core innovation.** The paper introduces **Context-ReAct**, an extension of ReAct in which the agent co-generates, at every step, four fields: a chain-of-thought, a list of *meta-operations* on its own context, a motivation, and a standard tool call. Five atomic meta-operations are defined: SKIP (no-op), COMPRESS (abstractive summary over an arbitrary contiguous step range), ROLLBACK (revert to step k with a recorded reason), SNIPPET (lossless pointer-based substring extraction), and DELETE (remove a step entirely). They instantiate the paradigm as **LongSeeker**, an SFT of Qwen3-30B-A3B on 10k trajectories synthesized by DeepSeek-V3.2 acting as teacher.

**Methodology — strengths:**
- Clean conceptual decomposition of context management into five typed primitives co-generated with reasoning.
- SNIPPET as pointer-based extraction sidesteps summarizer hallucination of numbers/URLs/entity names.
- Allowing COMPRESS over arbitrary [a,b] enables retroactive curation, a real capability gap relative to AgentFold.
- Empirical context-growth analysis (Fig 4a) shows token count plateauing ~15k vs linear blow-up for vanilla ReAct.

**Methodology — weaknesses:**
- The 'expressive completeness' theorem is essentially trivial — COMPRESS over the full history can produce any string, so completeness is by construction.
- No ablation removing individual operators (e.g., LongSeeker without ROLLBACK or SNIPPET).
- Training data fully distilled from one teacher (DeepSeek-V3.2) — student inherits teacher's heuristics with no rejection sampling or RL refinement.
- Only 200 questions sampled from BrowseComp / BrowseComp-ZH, widening confidence intervals on headline numbers.
- MiroThinker-1.7-mini at the same 30B scale outperforms LongSeeker on BrowseComp (67.9 vs 61.5) using CPT+SFT+RL — a fact under-emphasized in the narrative.

**Results.** LongSeeker-30B reaches BrowseComp 61.5, BrowseComp-ZH 62.5, xbench-2505 78.0, GAIA-text 77.7. Wins over Tongyi-DeepResearch and AgentFold; loses to MiroThinker-1.7-mini at the same 30B scale. The most informative result is the context-growth curve: LongSeeker stays under ~15k tokens out to ~300 turns while DeepSeek-V3.2-ReAct grows linearly.

**Why this is on your radar.** Highly relevant on three declared interests. (1) Agents and harnesses: Context-ReAct is precisely a harness-level design — it specifies the per-step structured output schema and how the harness mutates context between turns. (2) Tool use: meta-operations are themselves modeled as tool calls co-generated with standard tools. (3) Agent evaluation: BrowseComp, xbench, and GAIA are canonical long-horizon search-agent benchmarks; the Fig 4a context-growth analysis is a useful methodology template.

**Confidence:** medium-high.

**Connections:** AgentFold (Ye et al., 2025), ARC (Yao et al., 2026), MEM1 (Zhou et al., 2025), MemAgent (Yu et al., 2025), MiroThinker series, OpenSeeker (Du et al., 2026), original ReAct (Yao et al., 2023), BrowseComp (Wei et al., 2025), GAIA (Mialon et al., 2023).

---

### 2605.05007

**Background.** LLM multi-agent systems typically follow one of two rigid orchestration patterns: flat per-query model routing (a router picks one expert per query), or hand-engineered hierarchical task decomposition (a planner spawns sub-agents but assignment is prompt-driven or hardcoded). Across both, the decisions of *whether/how deeply to decompose* and *which expert to route each subtask to* are optimized in isolation. Prior work cited includes RouterDC, GraphRouter, ICL-Router, Router-R1, AgentOrchestra, ToolLLM, and on the RL side GRPO, Tree-GRPO, GiGPO.

**Core innovation.** Uno-Orchestra collapses task decomposition and per-subtask (model, primitive) routing into a single causal-LM policy that emits both within the same assistant turn. A "primitive" is the atomic routable action (direct_answer, reason, web_search, execute_python, symbolic_math) drawn from a closed vocabulary. Training is two-stage: (1) SFT on a verifier-gated curriculum of ~61k teacher-distilled trajectories with code/tool calls executed in real sandboxes; (2) Agentic-GRPO — a multi-turn extension of GRPO that distributes terminal verifier reward back to individual turns with bounded process-shaping signals.

**Methodology — strengths:**
- Unified policy avoids redundant context passes of separate planner+dispatcher modules.
- Verifier-gated curriculum cleanly separates SFT-able trajectories from RL-only residual hard pool.
- Agentic-GRPO addresses the multi-turn credit assignment problem with bounded shaping rewards.
- Blind-worker protocol prevents the router from exploiting brand-name shortcuts; ablation shows removing it inflates cost ~5x for <1pt accuracy gain.
- Comprehensive evaluation: 22 baselines across 13 benchmarks spanning 5 capability domains.
- Real-environment trajectories (sandboxed code execution) rather than simulated traces.

**Methodology — weaknesses:**
- Heavy reliance on a strong teacher orchestrator means the SFT upper bound is teacher quality.
- Cost metric (USD/q) depends on snapshot-in-time API tariffs from many providers; reproducibility of the cost frontier is fragile.
- The 13-benchmark macro-average is unweighted across heterogeneous domains, which can mask domain-specific weaknesses.
- Agentic-GRPO's per-turn shaping reward design (schema validity, repair indicator) is described but not ablated.
- Only one router backbone size (Qwen2.5-7B) is fully RL-trained; the 4B comparison shows non-trivial degradation.

**Results.** 77.0% macro pass@1 on the 13-benchmark suite, ~16 percentage points above AgentOrchestra (the strongest workflow baseline at ~67.2%), at $0.10/query vs AgentOrchestra's $1.21/query (~12x cheaper). Per-benchmark gains largest on AIME (+80% relative), LiveCodeBench (+55%), GPQA (+27%). Marginal/negative on GAIA (-1.7%) and SWE-bench (-0.7%). Stage ablation: Uno-base 48.1 -> SFT 61.3 -> GRPO 74.5 -> tree-GRPO 76.0 -> Agentic-GRPO 77.0, with the final stage *reducing* per-query cost from $0.171 to $0.101 while gaining 1pt — suggesting turn-level credit prunes redundant dispatches.

**Why this is on your radar.** Highly relevant given declared interests in agents/harnesses, tool use, and agent evaluation. The closed-vocabulary primitive set and XML trajectory grammar are concrete, implementable patterns. The 13-benchmark suite spans GAIA, Terminal-Bench, ToolBench. The Agentic-GRPO objective and credit-assignment discussion is a clean concrete extension of GRPO worth working through.

**Confidence:** medium-high.

**Connections:** GRPO (Shao et al., 2024), Tree-GRPO (Ji et al., 2025), Router-R1 (Zhang et al., NeurIPS 2025), AgentOrchestra (Zhang et al., 2025), ToolLLM (Qin et al., 2023), GAIA (Mialon et al., ICLR 2024).

---

## Skims (titles only — full triage scoring in run logs)

20 papers were triaged as 'skim': sufficient relevance for a one-line note but not a deep-read this cycle. The triage scoring blends keyword-match weight, recency, and a personalized you-model interest bonus.
