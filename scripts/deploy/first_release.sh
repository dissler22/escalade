#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "${SCRIPT_DIR}/common.sh"

SOURCE_DIR="${1:-}"

if [ -z "${SOURCE_DIR}" ]; then
    echo "Usage: $0 <source_dir> [release_id]" >&2
    exit 1
fi

load_env_file
ensure_layout
require_command "${PYTHON_BIN}"

RELEASE_ID="${2:-$(timestamp)}"
RELEASE_PATH="$(create_release_dir "${RELEASE_ID}")"

tar \
    --exclude=".git" \
    --exclude=".venv" \
    --exclude="__pycache__" \
    -cf - -C "${SOURCE_DIR}" . | tar -xf - -C "${RELEASE_PATH}"

if [ ! -x "${APP_VENV_PATH}/bin/python" ]; then
    "${PYTHON_BIN}" -m venv "${APP_VENV_PATH}"
fi

install_runtime_dependencies "${RELEASE_PATH}"

export DJANGO_SETTINGS_MODULE=config.settings
export PYTHONPATH="${RELEASE_PATH}/src"

"${APP_VENV_PATH}/bin/python" "${RELEASE_PATH}/src/manage.py" migrate --noinput
"${APP_VENV_PATH}/bin/python" "${RELEASE_PATH}/src/manage.py" collectstatic --noinput

activate_release "${RELEASE_PATH}"
log "first_release release_id=${RELEASE_ID} result=prepared"
