"""Typed configuration loaded from .env / environment variables.

Single source of truth — modules import get_settings(), not os.environ directly.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for Professor.Claude.AI.

    All values can be overridden via environment variables or a .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Required ---
    anthropic_api_key: str = Field(..., description="Claude API key")

    # --- Observability (recommended) ---
    langsmith_api_key: str | None = None
    langsmith_project: str = "professor-claude-ai"
    langsmith_tracing: bool = False

    # --- Email digest ---
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    digest_recipient: str | None = None

    # --- Local triage model (v0.2+) ---
    ollama_host: str = "http://localhost:11434"
    triage_model: str = "gemma2:9b"

    # --- Storage paths ---
    checkpoint_db_path: Path = Path("./data/checkpoints.sqlite")
    chroma_persist_dir: Path = Path("./data/chroma")
    episodic_db_path: Path = Path("./data/episodic.duckdb")

    # --- Runtime tunables ---
    max_deep_reads_per_run: int = Field(2, ge=1, le=10)
    subfield_keywords: str = "agent,agentic,harness,tool-use,scaffold"

    # --- Claude model selection ---
    deep_read_model: str = "claude-opus-4-7"
    synthesis_model: str = "claude-opus-4-7"

    @property
    def keyword_list(self) -> list[str]:
        """Parse comma-separated keywords into a list."""
        return [k.strip().lower() for k in self.subfield_keywords.split(",") if k.strip()]

    def ensure_data_dirs(self) -> None:
        """Create data directories if they don't exist. Called on startup."""
        self.checkpoint_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
        self.episodic_db_path.parent.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get the singleton settings instance.

    Cached so the .env file is only read once per process.
    """
    return Settings()  # type: ignore[call-arg]  # pydantic-settings reads from env
