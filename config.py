import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production-please")
    DATABASE_URL = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres123@localhost:5432/taskmanager",
    )
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE   = False
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 86400