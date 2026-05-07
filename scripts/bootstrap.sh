#!/usr/bin/env bash
# Bootstrap a development environment for Professor.Claude.AI.
# Idempotent: safe to re-run.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "==> Checking for uv..."
if ! command -v uv >/dev/null 2>&1; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

echo "==> Creating venv (Python 3.12)..."
uv venv --python 3.12

echo "==> Installing package + dev dependencies..."
uv pip install -e ".[dev]"

echo "==> Setting up .env from template (if missing)..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "    Created .env from .env.example. Edit it to add your API keys."
else
    echo "    .env already exists — leaving it alone."
fi

echo "==> Installing pre-commit hooks..."
source .venv/bin/activate
pre-commit install

echo ""
echo "Bootstrap complete."
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your ANTHROPIC_API_KEY"
echo "  2. Activate the venv: source .venv/bin/activate"
echo "  3. Run tests:         pytest"
echo "  4. Try a dry run:     professor-run --dry-run --dev"
