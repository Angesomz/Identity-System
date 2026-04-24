#!/usr/bin/env bash
# start_frontend.sh — Starts the INSA Identity System frontend
# Run from: ~/Desktop/detect/insa_identity_system
# Usage:  bash start_frontend.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/frontend"

echo "=========================================="
echo "  INSA Identity System — Frontend"
echo "=========================================="
echo "[INFO] Starting Vite dev server on http://localhost:5173 ..."
echo ""

npm run dev
