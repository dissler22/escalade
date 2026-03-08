from __future__ import annotations

import os
from pathlib import Path


_TRUTHY_VALUES = {"1", "true", "yes", "on"}
_FALSY_VALUES = {"0", "false", "no", "off"}


def get_str(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    if value is None:
        return default
    stripped = value.strip()
    return stripped if stripped else default


def get_bool(name: str, default: bool = False) -> bool:
    value = get_str(name)
    if value is None:
        return default
    lowered = value.lower()
    if lowered in _TRUTHY_VALUES:
        return True
    if lowered in _FALSY_VALUES:
        return False
    raise ValueError(f"Environment variable {name} must be a boolean value.")


def get_int(name: str, default: int | None = None) -> int | None:
    value = get_str(name)
    if value is None:
        return default
    return int(value)


def get_list(name: str, default: list[str] | None = None) -> list[str]:
    value = get_str(name)
    if value is None:
        return list(default or [])
    return [item.strip() for item in value.split(",") if item.strip()]


def get_path(name: str, default: Path | str | None = None) -> Path | None:
    value = get_str(name)
    if value is None:
        if default is None:
            return None
        return Path(default).expanduser()
    return Path(value).expanduser()
