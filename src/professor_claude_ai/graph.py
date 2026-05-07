"""LangGraph wiring for the nightly run.

For v0.1 we use a simple linear graph rather than the full Supervisor pattern.
Reasoning: the Supervisor (Manning ch 12.3) shines when there's genuine
multi-step coordination with branching. Our v0.1 flow is deterministic
(ingest → triage → deep_read → synthesize), so a linear StateGraph is simpler
and easier to debug. We migrate to the Supervisor in v0.2 when retries and
branching come in.

See docs/adr/0004-linear-graph-vs-supervisor-v01.md for the full justification.
"""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from professor_claude_ai.agents.deep_read import deep_read_node
from professor_claude_ai.agents.ingestion import ingestion_node
from professor_claude_ai.agents.synthesis import synthesis_node
from professor_claude_ai.agents.triage import triage_node
from professor_claude_ai.state import ProfessorState


def build_graph() -> StateGraph:
    """Build (uncompiled) the v0.1 nightly run graph.

    Caller compiles it with a checkpointer:

        with get_checkpointer(settings.checkpoint_db_path) as ckpt:
            app = build_graph().compile(checkpointer=ckpt)
            app.invoke(initial_state, config={"configurable": {"thread_id": run_id}})
    """
    g = StateGraph(ProfessorState)

    g.add_node("ingestion", ingestion_node)
    g.add_node("triage", triage_node)
    g.add_node("deep_read", deep_read_node)
    g.add_node("synthesis", synthesis_node)

    g.set_entry_point("ingestion")
    g.add_edge("ingestion", "triage")
    g.add_edge("triage", "deep_read")
    g.add_edge("deep_read", "synthesis")
    g.add_edge("synthesis", END)

    return g
