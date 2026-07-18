"""Render.com production settings for LegacyLens.

Zero secrets here — all sensitive values come from Render environment variables.
"""

import os

from .base import *  # noqa: F403, F401

# ------------------------------------------------------------------
# Core
# ------------------------------------------------------------------
DEBUG = False

# Render injects RENDER_EXTERNAL_HOSTNAME automatically
RENDER_HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "")

ALLOWED_HOSTS = [
    RENDER_HOST,
    ".onrender.com",
    "localhost",
    "127.0.0.1",
]

# Trust Render's TLS-terminating proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# CSRF — allow the Render subdomain
CSRF_TRUSTED_ORIGINS = [
    f"https://{RENDER_HOST}",
    "https://*.onrender.com",
]

# ------------------------------------------------------------------
# Security (Render handles TLS — no Django redirect needed)
# ------------------------------------------------------------------
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# ------------------------------------------------------------------
# Database
# ------------------------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL", "")

if DATABASE_URL:
    # Render free PostgreSQL — auto-provisioned when you add the add-on
    try:
        import dj_database_url

        DATABASES = {
            "default": dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                ssl_require=True,
            )
        }
    except ImportError:
        pass  # Falls through to SQLite below
else:
    # Fallback: SQLite (fine for demo/hackathon)
    DATABASES = {  # noqa: F405
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }

# ------------------------------------------------------------------
# Static files — WhiteNoise serves them without a CDN
# ------------------------------------------------------------------
MIDDLEWARE.insert(  # noqa: F405
    1, "whitenoise.middleware.WhiteNoiseMiddleware"
)
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

# ------------------------------------------------------------------
# Supermemory — reads SUPERMEMORY_API_KEY + SUPERMEMORY_BASE_URL
# from Render env vars. Set these to your Supermemory Cloud values.
# Local dev continues to use http://localhost:6767 via .env
# ------------------------------------------------------------------
# (No code needed — base.py already reads from env vars)

# ------------------------------------------------------------------
# LLM — reads OPENAI_API_KEY + OPENAI_BASE_URL + OPENAI_MODEL
# from Render env vars.
# ------------------------------------------------------------------
# (No code needed — base.py already reads from env vars)
