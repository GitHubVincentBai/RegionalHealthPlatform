#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DB_FILE="$ROOT_DIR/sql/000_regional_health_elder_database.sql"

DB_HOST="${ELDER_SERVICE_DB_HOST:-127.0.0.1}"
DB_PORT="${ELDER_SERVICE_DB_PORT:-5432}"
MAINTENANCE_DB="${ELDER_SERVICE_MAINTENANCE_DB:-postgres}"
DB_USER="${ELDER_SERVICE_DB_USER:-${USER:-postgres}}"
DB_PASSWORD="${ELDER_SERVICE_DB_PASSWORD:-}"

if [[ ! -f "$DB_FILE" ]]; then
  echo "database file not found: $DB_FILE" >&2
  exit 1
fi

export PGPASSWORD="$DB_PASSWORD"

echo "[elder-service] ensuring database exists via: $DB_FILE"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$MAINTENANCE_DB" -v ON_ERROR_STOP=1 -f "$DB_FILE"
echo "[elder-service] database regional_health_elder is ready"
