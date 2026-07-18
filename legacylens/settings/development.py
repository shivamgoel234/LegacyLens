"""
Development settings for LegacyLens.

Uses SQLite, DEBUG=True, permissive ALLOWED_HOSTS.
"""

import os

from .base import *  # noqa: F403, F401
from .base import BASE_DIR, LOGGING

# ---------------------------------------------------------------------------
# Development overrides
# ---------------------------------------------------------------------------
DEBUG = True

ALLOWED_HOSTS = ["*", "localhost", "127.0.0.1"]

# SQLite for local development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ---------------------------------------------------------------------------
# Development logging — more verbose
# ---------------------------------------------------------------------------
LOGGING["handlers"]["console"]["level"] = "DEBUG"
LOGGING["loggers"]["django"]["level"] = "INFO"
LOGGING["loggers"]["legacylens"]["level"] = "DEBUG"
LOGGING["root"]["level"] = "DEBUG"

# File handler for development logs
_log_dir = BASE_DIR / "logs"
_log_dir.mkdir(exist_ok=True)

LOGGING["handlers"]["dev_file"] = {
    "level": "DEBUG",
    "class": "logging.FileHandler",
    "filename": os.path.join(str(_log_dir), "legacylens-dev.log"),
    "formatter": "structured",
}

LOGGING["loggers"]["legacylens"]["handlers"].append("dev_file")
