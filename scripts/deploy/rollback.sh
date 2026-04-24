#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "${SCRIPT_DIR}/common.sh"

TARGET_RELEASE="${1:-}"
BACKUP_FILE="${2:-}"

load_env_file

if [ -z "${TARGET_RELEASE}" ]; then
    TARGET_RELEASE="$(basename "$(previous_release_path)")"
fi

TARGET_PATH="${APP_RELEASES_ROOT}/${TARGET_RELEASE}"
[ -d "${TARGET_PATH}" ] || {
    echo "Release not found: ${TARGET_PATH}" >&2
    exit 1
}

activate_release "${TARGET_PATH}"

if [ -n "${BACKUP_FILE}" ]; then
    "${SCRIPT_DIR}/restore_sqlite.sh" "${BACKUP_FILE}"
fi

restart_services

if [ -n "${SMOKE_FIRST_NAME:-}" ] && [ -n "${SMOKE_LAST_NAME:-}" ] && [ -n "${SMOKE_PASSWORD:-}" ]; then
    "${SCRIPT_DIR}/smoke_check.sh" "${SMOKE_BASE_URL:-http://34.71.54.146}"
fi

log "rollback release_id=${TARGET_RELEASE} backup=${BACKUP_FILE:-none} result=completed"
