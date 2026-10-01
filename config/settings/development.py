from .base import *  # noqa: F401,F403

load_dotenv(BASE_DIR / ".env.example")
SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

