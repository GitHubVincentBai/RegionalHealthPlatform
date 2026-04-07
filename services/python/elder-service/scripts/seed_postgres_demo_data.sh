#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SEED_FILE="$ROOT_DIR/sql/002_elder_mvp_seed.sql"

DB_HOST="${ELDER_SERVICE_DB_HOST:-127.0.0.1}"
DB_PORT="${ELDER_SERVICE_DB_PORT:-5432}"
DB_NAME="${ELDER_SERVICE_DB_NAME:-regional_health_elder}"
DB_USER="${ELDER_SERVICE_DB_USER:-${USER:-postgres}}"
DB_PASSWORD="${ELDER_SERVICE_DB_PASSWORD:-}"

if [[ ! -f "$SEED_FILE" ]]; then
  echo "seed file not found: $SEED_FILE" >&2
  exit 1
fi

export PGPASSWORD="$DB_PASSWORD"

echo "[elder-service] applying seed data: $SEED_FILE"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -f "$SEED_FILE"
echo "[elder-service] seed data applied successfully"
