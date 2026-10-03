"""Development settings for the RetroDoc backend."""

from .base import *  # noqa: F401,F403


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

DEBUG = True


# ---------------------------------------------------------------------------
# Hosts
# ---------------------------------------------------------------------------

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "192.168.16.125",
    "testserver"
]


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.16.125:3000",
    "http://localhost:3001",
]


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "smtp.gmail.com"

EMAIL_PORT = 587

EMAIL_USE_TLS = True

EMAIL_USE_SSL = False

EMAIL_HOST_USER = os.environ.get(
    "EMAIL_HOST_USER",
    "",
)

EMAIL_HOST_PASSWORD = os.environ.get(
    "EMAIL_HOST_PASSWORD",
    "",
)

DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    "RetroDoc <no-reply@retrodoc.local>",
)

SERVER_EMAIL = os.environ.get(
    "SERVER_EMAIL",
    DEFAULT_FROM_EMAIL,
)

EMAIL_SUBJECT_PREFIX = "[RetroDoc]"

EMAIL_TIMEOUT = 10


# ---------------------------------------------------------------------------
# Redis / Celery
# ---------------------------------------------------------------------------

REDIS_URL = os.environ.get(
    "REDIS_URL",
    "redis://localhost:6379/0",
)

CELERY_BROKER_URL = REDIS_URL

CELERY_RESULT_BACKEND = "django-db"

CELERY_ACCEPT_CONTENT = [
    "json",
]

CELERY_TASK_SERIALIZER = "json"

CELERY_RESULT_SERIALIZER = "json"

CELERY_TIMEZONE = "UTC"


# ---------------------------------------------------------------------------
# Development security
# ---------------------------------------------------------------------------

SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = False

CSRF_COOKIE_SECURE = False