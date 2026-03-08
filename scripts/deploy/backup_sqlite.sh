#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "${SCRIPT_DIR}/common.sh"

load_env_file
ensure_layout
require_command sqlite3

if [ ! -f "${APP_DATABASE_PATH}" ]; then
    echo "Database file not found: ${APP_DATABASE_PATH}" >&2
    exit 1
fi

backup_path="${APP_BACKUP_ROOT}/$(basename "${APP_DATABASE_PATH}" .sqlite3)-$(timestamp).sqlite3"
sqlite3 "${APP_DATABASE_PATH}" ".backup '${backup_path}'"

if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "${backup_path}" >"${backup_path}.sha256"
fi

log "backup_sqlite backup=${backup_path} result=completed"
printf '%s\n' "${backup_path}"
