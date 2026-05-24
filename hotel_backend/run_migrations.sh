#!/usr/bin/env bash
set -euo pipefail
# Create the PostgreSQL schema from the repository root of the backend
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
python render_migrate.py
