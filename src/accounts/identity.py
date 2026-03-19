import re
import unicodedata


TEMPORARY_ACCESS_CODE = "2026"

_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def _ascii_fold(value: str | None) -> str:
    normalized = unicodedata.normalize("NFKD", (value or "").strip())
    return normalized.encode("ascii", "ignore").decode("ascii").lower()


def build_lookup_key(value: str | None) -> str:
    return _NON_ALNUM_RE.sub("", _ascii_fold(value))


def build_login_key_from_full_name(full_name: str | None) -> str:
    return build_lookup_key(full_name)


def build_login_key_from_parts(first_name: str | None, last_name: str | None) -> str:
    return build_lookup_key(f"{first_name or ''} {last_name or ''}")
