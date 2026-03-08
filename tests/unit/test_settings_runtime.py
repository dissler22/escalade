import importlib

import pytest
from django.core.exceptions import ImproperlyConfigured


SETTINGS_KEYS = {
    "DJANGO_SECRET_KEY",
    "DJANGO_DEBUG",
    "DJANGO_ALLOWED_HOSTS",
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "DJANGO_USE_X_FORWARDED_HOST",
    "DJANGO_USE_PROXY_SSL_HEADER",
    "DJANGO_SECURE_SSL_REDIRECT",
    "DJANGO_SESSION_COOKIE_SECURE",
    "DJANGO_CSRF_COOKIE_SECURE",
    "APP_NAME",
    "APP_SHARED_ROOT",
    "APP_RELEASES_ROOT",
    "APP_CURRENT_LINK",
    "APP_ENV_FILE",
    "APP_DATABASE_PATH",
    "APP_STATIC_ROOT",
    "APP_LOG_PATH",
}


@pytest.fixture(autouse=True)
def clean_settings_env(monkeypatch):
    for key in SETTINGS_KEYS:
        monkeypatch.delenv(key, raising=False)


def load_settings(monkeypatch, **env_vars):
    for key, value in env_vars.items():
        monkeypatch.setenv(key, str(value))
    import config.settings as settings_module

    return importlib.reload(settings_module)


def test_production_settings_require_secret_key(monkeypatch):
    with pytest.raises(ImproperlyConfigured, match="DJANGO_SECRET_KEY"):
        load_settings(
            monkeypatch,
            DJANGO_DEBUG="false",
            DJANGO_ALLOWED_HOSTS="34.71.54.146",
        )


def test_production_settings_load_allowed_hosts_and_paths(monkeypatch, tmp_path):
    database_path = tmp_path / "db" / "escalade.sqlite3"
    static_root = tmp_path / "static"
    log_path = tmp_path / "log" / "django.log"

    settings = load_settings(
        monkeypatch,
        DJANGO_DEBUG="false",
        DJANGO_SECRET_KEY="production-secret",
        DJANGO_ALLOWED_HOSTS="34.71.54.146,escalade.example.org",
        APP_DATABASE_PATH=database_path,
        APP_STATIC_ROOT=static_root,
        APP_LOG_PATH=log_path,
    )

    assert settings.DEBUG is False
    assert settings.ALLOWED_HOSTS == ["34.71.54.146", "escalade.example.org"]
    assert settings.DATABASES["default"]["NAME"] == database_path
    assert settings.STATIC_ROOT == static_root
    assert settings.APP_LOG_PATH == log_path


def test_proxy_and_csrf_settings_are_externalized(monkeypatch):
    settings = load_settings(
        monkeypatch,
        DJANGO_SECRET_KEY="production-secret",
        DJANGO_DEBUG="false",
        DJANGO_ALLOWED_HOSTS="34.71.54.146",
        DJANGO_CSRF_TRUSTED_ORIGINS="https://escalade.example.org",
        DJANGO_USE_X_FORWARDED_HOST="true",
        DJANGO_USE_PROXY_SSL_HEADER="true",
        DJANGO_SECURE_SSL_REDIRECT="true",
        DJANGO_SESSION_COOKIE_SECURE="true",
        DJANGO_CSRF_COOKIE_SECURE="true",
    )

    assert settings.CSRF_TRUSTED_ORIGINS == ["https://escalade.example.org"]
    assert settings.USE_X_FORWARDED_HOST is True
    assert settings.SECURE_PROXY_SSL_HEADER == ("HTTP_X_FORWARDED_PROTO", "https")
    assert settings.SECURE_SSL_REDIRECT is True
    assert settings.SESSION_COOKIE_SECURE is True
    assert settings.CSRF_COOKIE_SECURE is True
