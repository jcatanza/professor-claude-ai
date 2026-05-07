"""Memory layer.

Two tiers:
- Short-term (within a run): LangGraph SqliteSaver checkpointer (Manning ch 14.1)
- Long-term (across runs): ChromaDB + DuckDB + the You-Model

v0.1 implements both at a basic level. v0.3 layers the four-layer Smallville-style
architecture on top.
"""
