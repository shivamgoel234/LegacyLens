"""Railway-optimized production settings for LegacyLens."""
import os
from .base import *  # noqa: F403, F401

DEBUG = False

# Railway sets RAILWAY_STATIC_URL, PORT, etc.
ALLOWED_HOSTS = [
    os.environ.get("RAILWAY_PUBLIC_DOMAIN", "*"),
    ".railway.app",
    "localhost",
    "127.0.0.1",
]

# Trust Railway's proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# CSRF — allow Railway domain
CSRF_TRUSTED_ORIGINS = [
    f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}",
    "https://*.railway.app",
]

# Security (Railway handles HTTPS)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Database — use PostgreSQL if DATABASE_URL set, else SQLite
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL:
    import dj_database_url
    DATABASES = {"default": dj_database_url.config(default=DATABASE_URL)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }

# Static files — WhiteNoise serves them in production
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
