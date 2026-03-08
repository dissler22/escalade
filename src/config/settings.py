from django.core.exceptions import ImproperlyConfigured
from pathlib import Path

from .env import get_bool, get_int, get_list, get_path, get_str


BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / "src"
DEFAULT_SECRET_KEY = "dev-only-secret-key"

SECRET_KEY = get_str("DJANGO_SECRET_KEY", default=DEFAULT_SECRET_KEY)
DEBUG = get_bool("DJANGO_DEBUG", default=True)
ALLOWED_HOSTS = get_list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
CSRF_TRUSTED_ORIGINS = get_list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])
USE_X_FORWARDED_HOST = get_bool("DJANGO_USE_X_FORWARDED_HOST", default=not DEBUG)
SECURE_PROXY_SSL_HEADER = (
    ("HTTP_X_FORWARDED_PROTO", "https")
    if get_bool("DJANGO_USE_PROXY_SSL_HEADER", default=not DEBUG)
    else None
)
SECURE_SSL_REDIRECT = get_bool("DJANGO_SECURE_SSL_REDIRECT", default=False)
SESSION_COOKIE_SECURE = get_bool("DJANGO_SESSION_COOKIE_SECURE", default=SECURE_SSL_REDIRECT)
CSRF_COOKIE_SECURE = get_bool("DJANGO_CSRF_COOKIE_SECURE", default=SECURE_SSL_REDIRECT)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

APP_NAME = get_str("APP_NAME", default="escalade")
APP_SHARED_ROOT = get_path("APP_SHARED_ROOT", default=BASE_DIR / ".runtime")
APP_RELEASES_ROOT = get_path("APP_RELEASES_ROOT", default=BASE_DIR / ".runtime" / "releases")
APP_CURRENT_LINK = get_path("APP_CURRENT_LINK", default=BASE_DIR / ".runtime" / "current")
APP_ENV_FILE = get_path("APP_ENV_FILE", default=BASE_DIR / ".env")
APP_DATABASE_PATH = get_path("APP_DATABASE_PATH", default=BASE_DIR / "db.sqlite3")
APP_STATIC_ROOT = get_path("APP_STATIC_ROOT", default=BASE_DIR / "staticfiles")
APP_LOG_PATH = get_path("APP_LOG_PATH")
NOTIFICATION_SENDER_EMAIL = get_str("APP_NOTIFICATION_SENDER_EMAIL", default="")
EMAIL_BACKEND = get_str(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = get_str("DJANGO_EMAIL_HOST", default="")
EMAIL_PORT = get_int("DJANGO_EMAIL_PORT", default=587)
EMAIL_HOST_USER = get_str("DJANGO_EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = get_str("DJANGO_EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = get_bool("DJANGO_EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = NOTIFICATION_SENDER_EMAIL or get_str(
    "DJANGO_DEFAULT_FROM_EMAIL",
    default="no-reply@example.invalid",
)
SERVER_EMAIL = DEFAULT_FROM_EMAIL

if SECRET_KEY == DEFAULT_SECRET_KEY and not DEBUG:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set outside debug mode.")

if not ALLOWED_HOSTS and not DEBUG:
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS must list at least one production host.")

if "*" in ALLOWED_HOSTS and not DEBUG:
    raise ImproperlyConfigured("Wildcard hosts are not allowed outside debug mode.")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts.apps.AccountsConfig",
    "sessions.apps.ClubSessionsConfig",
    "bookings.apps.BookingsConfig",
    "audit.apps.AuditConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [SRC_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": APP_DATABASE_PATH,
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [SRC_DIR / "static"]
STATIC_ROOT = APP_STATIC_ROOT

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

if APP_LOG_PATH is not None:
    LOGGING["handlers"]["file"] = {
        "class": "logging.FileHandler",
        "filename": str(APP_LOG_PATH),
        "formatter": "standard",
    }
    LOGGING["root"]["handlers"].append("file")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "sessions:session-list"
LOGOUT_REDIRECT_URL = "accounts:login"
