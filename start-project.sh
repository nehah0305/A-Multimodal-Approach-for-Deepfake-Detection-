#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Deepfake Detection Dashboard"
echo "Full Project Startup"
echo "=========================================="

python3 run_project.py
