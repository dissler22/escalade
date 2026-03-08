#!/usr/bin/env bash

set -euo pipefail

APP_NAME="${APP_NAME:-escalade}"
APP_USER="${APP_USER:-escalade}"
APP_GROUP="${APP_GROUP:-www-data}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
APP_ROOT="${APP_ROOT:-/srv/${APP_NAME}}"
GUNICORN_BIND="${GUNICORN_BIND:-127.0.0.1:8001}"
GUNICORN_WORKERS="${GUNICORN_WORKERS:-3}"
SYSTEMD_SERVICE_NAME="${SYSTEMD_SERVICE_NAME:-escalade}"

refresh_layout_defaults() {
    APP_SHARED_ROOT="${APP_SHARED_ROOT:-${APP_ROOT}/shared}"
    APP_RELEASES_ROOT="${APP_RELEASES_ROOT:-${APP_ROOT}/releases}"
    APP_CURRENT_LINK="${APP_CURRENT_LINK:-${APP_ROOT}/current}"
    APP_ENV_FILE="${APP_ENV_FILE:-${APP_SHARED_ROOT}/config/${APP_NAME}.env}"
    APP_DATABASE_PATH="${APP_DATABASE_PATH:-${APP_SHARED_ROOT}/db/${APP_NAME}.sqlite3}"
    APP_STATIC_ROOT="${APP_STATIC_ROOT:-${APP_SHARED_ROOT}/static}"
    APP_LOG_PATH="${APP_LOG_PATH:-${APP_SHARED_ROOT}/log/django.log}"
    APP_OPERATIONS_LOG_PATH="${APP_OPERATIONS_LOG_PATH:-${APP_SHARED_ROOT}/log/operations.log}"
    APP_BACKUP_ROOT="${APP_BACKUP_ROOT:-${APP_SHARED_ROOT}/backups}"
    APP_VENV_PATH="${APP_VENV_PATH:-${APP_SHARED_ROOT}/venv}"
}

load_env_file() {
    if [ -f "${APP_ENV_FILE}" ]; then
        set -a
        # shellcheck disable=SC1090
        . "${APP_ENV_FILE}"
        set +a
    fi
    refresh_layout_defaults
}

timestamp() {
    date +"%Y%m%d%H%M%S"
}

log() {
    local message="$1"
    local log_dir
    log_dir="$(dirname "${APP_OPERATIONS_LOG_PATH}")"
    mkdir -p "${log_dir}"
    printf '%s %s\n' "$(date +"%Y-%m-%dT%H:%M:%S%z")" "${message}" | tee -a "${APP_OPERATIONS_LOG_PATH}"
}

require_command() {
    local command_name="$1"
    command -v "${command_name}" >/dev/null 2>&1 || {
        echo "Missing required command: ${command_name}" >&2
        exit 1
    }
}

require_env() {
    local name="$1"
    local value="${!name:-}"
    if [ -z "${value}" ]; then
        echo "Missing required environment variable: ${name}" >&2
        exit 1
    fi
}

ensure_layout() {
    mkdir -p \
        "${APP_RELEASES_ROOT}" \
        "${APP_SHARED_ROOT}/config" \
        "${APP_SHARED_ROOT}/db" \
        "${APP_SHARED_ROOT}/static" \
        "${APP_SHARED_ROOT}/log" \
        "${APP_BACKUP_ROOT}"
}

create_release_dir() {
    local release_id="$1"
    local release_path="${APP_RELEASES_ROOT}/${release_id}"
    mkdir -p "${release_path}"
    printf '%s\n' "${release_path}"
}

current_release_path() {
    if [ -L "${APP_CURRENT_LINK}" ]; then
        readlink -f "${APP_CURRENT_LINK}"
    fi
}

previous_release_path() {
    local current_path
    current_path="$(current_release_path)"
    ls -1dt "${APP_RELEASES_ROOT}"/* 2>/dev/null | while read -r candidate; do
        if [ "${candidate}" != "${current_path}" ]; then
            printf '%s\n' "${candidate}"
            break
        fi
    done
}

activate_release() {
    local release_path="$1"
    ln -sfn "${release_path}" "${APP_CURRENT_LINK}"
}

restart_services() {
    systemctl daemon-reload
    systemctl restart "${SYSTEMD_SERVICE_NAME}"
    systemctl restart nginx
}

install_runtime_dependencies() {
    local project_root="$1"
    "${APP_VENV_PATH}/bin/python" - <<'PY' "${project_root}"
import subprocess
import sys
import tomllib
from pathlib import Path

project_root = Path(sys.argv[1])
pyproject = tomllib.loads((project_root / "pyproject.toml").read_text())
dependencies = pyproject["project"]["dependencies"]
subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
subprocess.check_call([sys.executable, "-m", "pip", "install", *dependencies])
PY
}

refresh_layout_defaults
