#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "${SCRIPT_DIR}/common.sh"

if [ "${EUID}" -ne 0 ]; then
    echo "Run this script with sudo." >&2
    exit 1
fi

apt-get update
apt-get install -y python3 python3-venv python3-pip nginx sqlite3 curl

if ! id -u "${APP_USER}" >/dev/null 2>&1; then
    useradd --system --create-home --home-dir "${APP_ROOT}" --shell /bin/bash "${APP_USER}"
fi

ensure_layout
chown -R "${APP_USER}:${APP_GROUP}" "${APP_ROOT}" "${APP_SHARED_ROOT}" "${APP_RELEASES_ROOT}"
chmod 0750 "${APP_ROOT}" "${APP_SHARED_ROOT}" "${APP_RELEASES_ROOT}" "${APP_SHARED_ROOT}/db" "${APP_SHARED_ROOT}/static" "${APP_SHARED_ROOT}/log" "${APP_BACKUP_ROOT}"

if [ ! -f "${APP_ENV_FILE}" ]; then
    install -o "${APP_USER}" -g "${APP_GROUP}" -m 0640 /dev/null "${APP_ENV_FILE}"
fi

log "provision_vm host=$(hostname) result=completed"
