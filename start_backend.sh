#!/usr/bin/env bash
# start_backend.sh — Starts the INSA Identity System backend
# Run from: ~/Desktop/detect/insa_identity_system
# Usage:  bash start_backend.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  INSA Identity System — Backend"
echo "=========================================="

# Always use 'python -m uvicorn' to bypass the broken launcher script
PYTHON_CMD=""
for cmd in python python3; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON_CMD="$cmd"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "[ERROR] Python not found. Make sure Python 3.10+ is installed."
    exit 1
fi

echo "[INFO] Using Python: $($PYTHON_CMD --version)"
echo "[INFO] Starting FastAPI server on http://localhost:8000 ..."
echo "[INFO] API docs: http://localhost:8000/docs"
echo ""

$PYTHON_CMD -m uvicorn gateway.main:app --reload --port 8000 --host 0.0.0.0
