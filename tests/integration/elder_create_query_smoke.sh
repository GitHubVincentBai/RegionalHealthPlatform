#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"

echo "[elder-smoke] backend create -> list -> detail"
(
  cd "$ROOT_DIR/services/python/elder-service"
  PYTHONPATH=src python3 -m unittest \
    tests.test_service.ElderServiceTest.test_create_list_and_fetch_profile_smoke
)

echo "[elder-smoke] frontend create -> list -> detail"
(
  cd "$ROOT_DIR/apps/web"
  node --test ./src/api/adapters/elder-service/flow.spec.mjs
)

echo "[elder-smoke] Elder intake P0 smoke passed"
