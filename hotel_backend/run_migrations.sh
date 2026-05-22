#!/usr/bin/env bash
set -euo pipefail
# Run Alembic migrations from the repository root of the backend
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
alembic upgrade head
