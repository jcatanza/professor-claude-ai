"""Command-line entry points.

`professor` — top-level CLI dispatcher
`professor-run` — runs a single nightly cycle (called by GitHub Actions)
"""

from __future__ import annotations

import argparse
import logging
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

from langchain_core.runnables import RunnableConfig

from professor_claude_ai.config import get_settings
from professor_claude_ai.graph import build_graph
from professor_claude_ai.logging_setup import configure_logging
from professor_claude_ai.memory.checkpointer import get_checkpointer
from professor_claude_ai.memory.you_model import YouModel
from professor_claude_ai.state import ProfessorState

logger = logging.getLogger(__name__)


def run_nightly(argv: list[str] | None = None) -> int:
    """Run a single nightly cycle. Returns process exit code."""
    parser = argparse.ArgumentParser(description="Run one nightly Professor.Claude.AI cycle")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip email/repo emission; print digest to stdout only",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Use human-readable console logs instead of JSON",
    )
    parser.add_argument(
        "--you-model-path",
        type=Path,
        default=Path("./data/you_model.json"),
    )
    args = parser.parse_args(argv)

    configure_logging(dev=args.dev)
    settings = get_settings()
    settings.ensure_data_dirs()

    you = YouModel(args.you_model_path)
    snapshot = you.snapshot()

    run_id = str(uuid.uuid4())
    run_date = datetime.now(UTC).date().isoformat()

    initial_state: ProfessorState = {
        "run_id": run_id,
        "run_date": run_date,
        "messages": [],
        "current_agent": None,
        "agent_history": [],
        "candidate_papers": [],
        "triage_decisions": [],
        "deep_reads": [],
        "you_model_snapshot": snapshot,
        "daily_digest": None,
        "verification_flags": [],
        "iteration_count": 0,
    }

    logger.info("starting nightly run %s on %s", run_id, run_date)

    with get_checkpointer(settings.checkpoint_db_path) as ckpt:
        app = build_graph().compile(checkpointer=ckpt)
        config: RunnableConfig = {"configurable": {"thread_id": run_id}}
        # langgraph's compile() does not propagate StateT to the resulting
        # Pregel, so mypy does not know app.invoke accepts ProfessorState.
        # The runtime type is correct.
        result = app.invoke(initial_state, config=config)  # type: ignore[arg-type]

    digest = result.get("daily_digest") or "(no digest produced)"

    if args.dry_run:
        print("\n========== DIGEST (dry-run) ==========\n")
        print(digest)
        return 0

    # TODO(v0.1.5): wire up email and GitHub commit emission here.
    # For now, write to local file.
    out_dir = Path("./data/digests")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"digest_{run_date}.md"
    out_path.write_text(digest)
    logger.info("wrote digest to %s", out_path)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Top-level CLI dispatcher (placeholder for additional subcommands)."""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(prog="professor")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run", help="Run a single nightly cycle")

    args, rest = parser.parse_known_args(argv)
    if args.cmd == "run":
        return run_nightly(rest)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
