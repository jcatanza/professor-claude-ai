"""The You-Model: persistent representation of the user's interests, knowledge,
and engagement history.

v0.1 — minimal: declared interests, current courses, current reading, simple
thumbs up/down log. Backed by a single JSON file for now (DuckDB integration
in v0.3).

v0.3 — full: knowledge state with concepts and depth, engagement signals,
spaced-repetition flags, evolving inferred interests.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from professor_claude_ai.state import YouModelSnapshot


class YouModel:
    """Persistent representation of the user.

    v0.1: file-backed, hand-edited JSON for declared fields; thumbs-up/down
    appended programmatically. Read snapshot for each run; write feedback
    after each run.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write_default()

    def _write_default(self) -> None:
        default: dict[str, Any] = {
            "declared_interests": [
                "agents and harnesses",
                "tool use",
                "agent evaluation",
            ],
            "current_courses": [
                "Modern Software Concepts (May 18 start)",
                "LLMs Theory and Practice",
                "Generative AI",
            ],
            "current_reading": [
                "Manning: AI Agents and Applications (Roberto Infante, 2026)",
                "Manning: Domain-Specific Small Language Models (queued)",
                "Manning: Build Python Web Apps with Streamlit (queued)",
            ],
            "feedback_log": [],
        }
        self.path.write_text(json.dumps(default, indent=2))

    def _read(self) -> dict[str, Any]:
        data: dict[str, Any] = json.loads(self.path.read_text())
        return data

    def _write(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, indent=2))

    def snapshot(self) -> YouModelSnapshot:
        """Get a frozen view for one run.

        Recent thumbs-up/down are limited to the last 50 entries each.
        """
        data = self._read()
        log = data.get("feedback_log", [])
        recent_up = [e["arxiv_id"] for e in log if e["vote"] == "up"][-50:]
        recent_down = [e["arxiv_id"] for e in log if e["vote"] == "down"][-50:]
        return YouModelSnapshot(
            declared_interests=data.get("declared_interests", []),
            current_courses=data.get("current_courses", []),
            current_reading=data.get("current_reading", []),
            recent_thumbs_up_arxiv_ids=recent_up,
            recent_thumbs_down_arxiv_ids=recent_down,
        )

    def record_feedback(self, arxiv_id: str, vote: str, note: str = "") -> None:
        """Record a thumbs up/down on a paper.

        vote must be 'up' or 'down'.
        """
        if vote not in {"up", "down"}:
            raise ValueError(f"vote must be 'up' or 'down', got {vote!r}")
        data = self._read()
        data.setdefault("feedback_log", []).append(
            {
                "arxiv_id": arxiv_id,
                "vote": vote,
                "note": note,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )
        self._write(data)
