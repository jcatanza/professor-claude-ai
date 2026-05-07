"""LangGraph SqliteSaver checkpointer — short-term (within-run) memory.

Per Manning AI Agents and Applications ch 14.1: gives us free state rehydration
on failure (a real concern for unattended overnight jobs). Replaces the book's
InMemorySaver, which the book itself flags as dev-only.
"""

from __future__ import annotations

from contextlib import AbstractContextManager
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver


def get_checkpointer(db_path: Path) -> AbstractContextManager[SqliteSaver]:
    """Get a SqliteSaver checkpointer context manager at the given path.

    Creates the parent directory if needed. `SqliteSaver.from_conn_string` is
    decorated with @contextmanager, so it returns a context manager that
    yields a SqliteSaver. The caller must use it with a `with` block.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return SqliteSaver.from_conn_string(str(db_path))
