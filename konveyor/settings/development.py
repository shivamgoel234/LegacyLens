import os

from .base import *  # noqa: F403, F401

# Import the base LOGGING dict to modify it
from .base import LOGGING

# Development settings
DEBUG = True
# Allow localhost and any ngrok domains for development
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Add any ngrok domains from environment variables
NGROK_URL = os.environ.get("NGROK_URL", "")
if NGROK_URL:
    # Extract the domain from the URL (e.g., 'abc123.ngrok.io' from 'https://abc123.ngrok.io')  # noqa: E501
    from urllib.parse import urlparse

    ngrok_domain = urlparse(NGROK_URL).netloc or urlparse(NGROK_URL).path
    if ngrok_domain:
        ALLOWED_HOSTS.append(ngrok_domain)
        print(f"Added ngrok domain to ALLOWED_HOSTS: {ngrok_domain}")

# For convenience during development, also allow all ngrok-free.app domains
ALLOWED_HOSTS.extend(
    [
        "3588-2601-195-c902-7c10-5db7-9304-5464-d604.ngrok-free.app",
        "ngrok-free.app",
        "*.ngrok-free.app",
    ]
)

# Use SQLite for development for simplicity
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# Debug Toolbar Configuration (temporarily disabled for testing)
# INSTALLED_APPS += [
#     'debug_toolbar',
# ]

# MIDDLEWARE += [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ]

INTERNAL_IPS = [
    "127.0.0.1",
]

# Enable django extensions if installed
try:
    import django_extensions  # noqa: F401

    INSTALLED_APPS += ["django_extensions"]  # noqa: F405
except ImportError:
    pass

# Development Logging Configuration (modifies base LOGGING)
# Ensure LOGGING_FORMATTERS and LOGGING_HANDLERS are available if directly referenced
# or rely on them being part of the imported LOGGING structure from base.

LOGGING["handlers"]["console"]["level"] = "DEBUG"
LOGGING["loggers"]["django"]["level"] = "DEBUG"  # More verbose Django logs for dev
LOGGING["loggers"]["konveyor"]["level"] = "DEBUG"
LOGGING["root"]["level"] = "DEBUG"

# Add development-specific file handler
LOGGING["handlers"]["dev_file"] = {
    "level": "DEBUG",
    "class": "logging.FileHandler",
    "filename": os.path.join(
        BASE_DIR,
        "logs",
        "konveyor-dev.log",  # noqa: F405
    ),
    "formatter": "structured",  # Assumes 'structured' formatter is in base LOGGING_FORMATTERS
}

# Add the dev_file handler to relevant loggers
if "dev_file" not in LOGGING["loggers"]["konveyor"]["handlers"]:
    LOGGING["loggers"]["konveyor"]["handlers"].append("dev_file")
if "dev_file" not in LOGGING["root"]["handlers"]:
    LOGGING["root"]["handlers"].append("dev_file")

# For specific sub-modules if you want them to also log to file:
# Example: Ensure bot logs go to the dev file as well
if "konveyor.apps.bot" not in LOGGING["loggers"]:
    LOGGING["loggers"]["konveyor.apps.bot"] = {
        "handlers": ["console", "dev_file"],
        "level": "DEBUG",
        "propagate": False,  # Typically False if you define specific handlers
    }
else:
    if "dev_file" not in LOGGING["loggers"]["konveyor.apps.bot"]["handlers"]:
        LOGGING["loggers"]["konveyor.apps.bot"]["handlers"].append("dev_file")
    LOGGING["loggers"]["konveyor.apps.bot"]["level"] = "DEBUG"
    LOGGING["loggers"]["konveyor.apps.bot"]["propagate"] = False

# Ensure other specific konveyor loggers also get the dev_file handler if desired
for logger_name in ["konveyor.core.slack", "konveyor.core.agent", "konveyor.core.chat"]:
    if logger_name not in LOGGING["loggers"]:
        LOGGING["loggers"][logger_name] = {
            "handlers": ["console", "dev_file"],
            "level": "DEBUG",
            "propagate": False,
        }
    else:
        if "dev_file" not in LOGGING["loggers"][logger_name]["handlers"]:
            LOGGING["loggers"][logger_name]["handlers"].append("dev_file")
        LOGGING["loggers"][logger_name]["level"] = "DEBUG"
        LOGGING["loggers"][logger_name]["propagate"] = False
