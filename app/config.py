from __future__ import annotations

import os
from pathlib import Path
from typing import Type

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base application configuration."""

    SECRET_KEY: bytes | str = os.environ.get("FLASK_SECRET_KEY", "")
    if not SECRET_KEY:
        # Fallback for local/dev when no env var is set; not checked into code.
        SECRET_KEY = os.urandom(32)

    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'spam_classifier.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    SESSION_COOKIE_SECURE: bool = (
        os.environ.get("SESSION_COOKIE_SECURE", "true").lower() == "true"
    )
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")

    WTF_CSRF_TIME_LIMIT = None

    MODEL_DIR: Path = Path(os.environ.get("MODEL_DIR", BASE_DIR))

    TESTING: bool = False


class TestingConfig(Config):
    """Configuration used by the pytest test suite."""

    TESTING: bool = True
    WTF_CSRF_ENABLED: bool = False
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    SESSION_COOKIE_SECURE: bool = False


def get_config() -> Type[Config]:
    """Return the configuration class based on FLASK_ENV."""
    env = os.environ.get("FLASK_ENV", "production").lower()
    if env == "testing":
        return TestingConfig
    return Config
