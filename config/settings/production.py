from .base import *  # noqa: F401,F403

DEBUG = False

CORS_ALLOWED_ORIGINS = [
    "https://retrodoc.exemple.com",
]

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True