#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${REPO_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)}"

exec bash "${ROOT_DIR}/tests/integration/elder_create_query_smoke.sh"
