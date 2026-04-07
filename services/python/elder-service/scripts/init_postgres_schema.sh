#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCHEMA_FILE="$ROOT_DIR/sql/001_elder_mvp_schema.sql"

DB_HOST="${ELDER_SERVICE_DB_HOST:-127.0.0.1}"
DB_PORT="${ELDER_SERVICE_DB_PORT:-5432}"
DB_NAME="${ELDER_SERVICE_DB_NAME:-regional_health_elder}"
DB_USER="${ELDER_SERVICE_DB_USER:-${USER:-postgres}}"
DB_PASSWORD="${ELDER_SERVICE_DB_PASSWORD:-}"

if [[ ! -f "$SCHEMA_FILE" ]]; then
  echo "schema file not found: $SCHEMA_FILE" >&2
  exit 1
fi

export PGPASSWORD="$DB_PASSWORD"

echo "[elder-service] applying schema: $SCHEMA_FILE"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -f "$SCHEMA_FILE"
echo "[elder-service] schema applied successfully"
