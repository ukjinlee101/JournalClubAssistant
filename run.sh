#!/bin/bash
# Journal Club Assistant — convenience runner
# Usage:
#   ./run.sh [--days N] [--output FILE] [--no-review]
#
# This script auto-detects whether to use Docker or a local venv.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── Try Docker first ────────────────────────────────────────────────────
if command -v docker &> /dev/null && docker info &> /dev/null 2>&1; then
    IMAGE_NAME="journal-club-assistant"

    # Build image if it doesn't exist or Dockerfile changed
    if ! docker image inspect "$IMAGE_NAME" &> /dev/null; then
        echo "🔨 Building Docker image (first run only)..."
        docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"
    fi

    # Run with interactive terminal (-it) and mount config + output
    docker run --rm -it \
        -v "$SCRIPT_DIR/config.yaml:/app/config.yaml:ro" \
        -v "$SCRIPT_DIR:/app/output" \
        -w /app/output \
        "$IMAGE_NAME" "$@"
    exit $?
fi

# ── Fallback: use local venv ────────────────────────────────────────────
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "📦 Setting up virtual environment (first run only)..."
    python3 -m venv "$SCRIPT_DIR/.venv"
    source "$SCRIPT_DIR/.venv/bin/activate"
    pip install -r "$SCRIPT_DIR/requirements.txt"
else
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

cd "$SCRIPT_DIR"
python -m src.main "$@"
