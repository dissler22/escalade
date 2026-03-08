#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "${SCRIPT_DIR}/common.sh"

BACKUP_FILE="${1:-}"

if [ -z "${BACKUP_FILE}" ]; then
    echo "Usage: $0 <backup_file>" >&2
    exit 1
fi

load_env_file

[ -f "${BACKUP_FILE}" ] || {
    echo "Backup file not found: ${BACKUP_FILE}" >&2
    exit 1
}

systemctl stop "${SYSTEMD_SERVICE_NAME}" || true
install -o "${APP_USER}" -g "${APP_GROUP}" -m 0640 "${BACKUP_FILE}" "${APP_DATABASE_PATH}"
systemctl start "${SYSTEMD_SERVICE_NAME}" || true

log "restore_sqlite backup=${BACKUP_FILE} result=completed"
