#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "${SCRIPT_DIR}/common.sh"

load_env_file
require_command curl
require_command python3

BASE_URL="${1:-http://34.71.54.146}"
SMOKE_EMAIL="${SMOKE_EMAIL:-}"
SMOKE_PASSWORD="${SMOKE_PASSWORD:-}"

if [ -z "${SMOKE_EMAIL}" ] || [ -z "${SMOKE_PASSWORD}" ]; then
    echo "SMOKE_EMAIL and SMOKE_PASSWORD are required." >&2
    exit 1
fi

cookie_jar="$(mktemp)"
login_page="$(mktemp)"
trap 'rm -f "${cookie_jar}" "${login_page}"' EXIT

check_status() {
    local url="$1"
    local expected="$2"
    local status
    status="$(curl -sS -o /dev/null -w '%{http_code}' "$url")"
    [ "${status}" = "${expected}" ] || {
        echo "Unexpected status for ${url}: ${status} (expected ${expected})" >&2
        exit 1
    }
}

root_status="$(curl -sS -o /dev/null -w '%{http_code}' "${BASE_URL}/")"
case "${root_status}" in
    301|302) ;;
    *)
        echo "Unexpected root status for ${BASE_URL}/: ${root_status}" >&2
        exit 1
        ;;
esac

check_status "${BASE_URL}/login/" "200"
check_status "${BASE_URL}/static/css/app.css" "200"

curl -sS -c "${cookie_jar}" "${BASE_URL}/login/" >"${login_page}"
csrf_token="$(
    python3 - <<'PY' "${login_page}"
import re
import sys
from pathlib import Path

content = Path(sys.argv[1]).read_text()
match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
if not match:
    raise SystemExit(1)
print(match.group(1))
PY
)"

login_status="$(curl -sS -o /dev/null -w '%{http_code}' \
    -b "${cookie_jar}" \
    -c "${cookie_jar}" \
    -e "${BASE_URL}/login/" \
    -X POST "${BASE_URL}/login/" \
    --data-urlencode "email=${SMOKE_EMAIL}" \
    --data-urlencode "password=${SMOKE_PASSWORD}" \
    --data-urlencode "csrfmiddlewaretoken=${csrf_token}")"
[ "${login_status}" = "302" ] || {
    echo "Login failed with status ${login_status}" >&2
    exit 1
}

sessions_status="$(curl -sS -o /dev/null -w '%{http_code}' -b "${cookie_jar}" "${BASE_URL}/sessions/")"
[ "${sessions_status}" = "200" ] || {
    echo "Sessions page failed with status ${sessions_status}" >&2
    exit 1
}

bookings_status="$(curl -sS -o /dev/null -w '%{http_code}' -b "${cookie_jar}" "${BASE_URL}/bookings/mine/")"
[ "${bookings_status}" = "200" ] || {
    echo "My bookings page failed with status ${bookings_status}" >&2
    exit 1
}

log "smoke_check base_url=${BASE_URL} result=passed"
