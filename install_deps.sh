#!/usr/bin/env bash
# install_deps.sh — Install all Python dependencies for INSA Identity System
# Run once before starting the backend.
# Usage:  bash install_deps.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  INSA Identity System — Install Deps"
echo "=========================================="

PYTHON_CMD=""
for cmd in python python3; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON_CMD="$cmd"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "[ERROR] Python not found."
    exit 1
fi

echo "[INFO] Using: $($PYTHON_CMD --version)"
echo "[INFO] Installing base requirements..."
$PYTHON_CMD -m pip install -r requirements.txt

echo ""
echo "[INFO] Installing OCR dependencies..."
$PYTHON_CMD -m pip install easyocr Pillow "google-generativeai>=0.7.0"

echo ""
echo "=========================================="
echo "  All dependencies installed successfully!"
echo "  Run:  bash start_backend.sh"
echo "=========================================="
