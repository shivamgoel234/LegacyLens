import logging
import os

from .base import *  # noqa: F403, F401

# Import the base LOGGING dict to potentially modify it

logger = logging.getLogger(__name__)

DEBUG = False
ALLOWED_HOSTS = [os.environ.get("WEBSITE_HOSTNAME", "*")]

# Security settings for production
# Disable SSL redirect when running in Azure App Service
# Azure App Service handles HTTPS redirects at the platform level
if os.environ.get(
    "WEBSITE_HOSTNAME"
):  # This environment variable is set in Azure App Service
    SECURE_SSL_REDIRECT = False
    logger.info("Running in Azure App Service, disabling SSL redirect")
else:
    SECURE_SSL_REDIRECT = (
        os.environ.get("SECURE_SSL_REDIRECT", "True").lower() == "true"
    )

SESSION_COOKIE_SECURE = (
    os.environ.get("SESSION_COOKIE_SECURE", "True").lower() == "true"
)
CSRF_COOKIE_SECURE = os.environ.get("CSRF_COOKIE_SECURE", "True").lower() == "true"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Azure-specific settings with defaults for testing
AZURE_OPENAI_ENDPOINT = os.environ.get(
    "AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com"
)
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "dummy-key")
AZURE_STORAGE_CONNECTION_STRING = os.environ.get(
    "AZURE_STORAGE_CONNECTION_STRING",
    "DefaultEndpointsProtocol=https;AccountName=example;AccountKey=example;EndpointSuffix=core.windows.net",  # noqa: E501
)
AZURE_SEARCH_ENDPOINT = os.environ.get(
    "AZURE_SEARCH_ENDPOINT", "https://example.search.windows.net"
)

# Database configuration with fallback to SQLite
# Try to use PostgreSQL first, but fall back to SQLite if connection fails
try:
    # Test PostgreSQL connection
    import psycopg2

    conn = psycopg2.connect(
        dbname=os.environ.get("DB_NAME", "legacylens"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "postgres"),
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", "5432"),
        connect_timeout=3,  # Short timeout for quick failure
    )
    conn.close()

    # If connection succeeds, use PostgreSQL
    logger.info("Successfully connected to PostgreSQL, using it as database backend")
    # Database settings are inherited from base.py

except Exception as e:
    # If connection fails, use SQLite
    logger.warning(f"Failed to connect to PostgreSQL: {str(e)}. Falling back to SQLite")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }

# Production Logging Configuration (modifies base LOGGING if needed)
# By default, it will use the INFO level console logging from base.py.
# Add production-specific handlers or level overrides here if necessary.
# For example, to add a production file log:
# LOGGING["handlers"]["prod_file"] = {
#     "level": "INFO",
#     "class": "logging.handlers.RotatingFileHandler", # Example: Rotating file handler
#     "filename": os.path.join(BASE_DIR, "logs", "legacylens-prod.log"), # noqa: F405
#     "maxBytes": 1024 * 1024 * 5,  # 5 MB
#     "backupCount": 5,
#     "formatter": "structured",
# }
# if "prod_file" not in LOGGING["loggers"]["legacylens"]["handlers"]:
#     LOGGING["loggers"]["legacylens"]["handlers"].append("prod_file")
# if "prod_file" not in LOGGING["root"]["handlers"]:
#     LOGGING["root"]["handlers"].append("prod_file")

# It's generally good practice for production to ensure critical/error logs are captured reliably.
# The base console handler at INFO level should be picked up by Azure Log Stream / Application Insights.

# Ensure sensitive information is not logged in production if DEBUG was ever True in base
if DEBUG:
    logger.warning(
        "DEBUG is True in a production environment settings file. Ensure this is not the case in actual production."
    )
    # Potentially strip or reduce verbosity of certain loggers if DEBUG was True from base

# TODO: Configure Azure Database for PostgreSQL
# TODO: Configure Azure Blob Storage for static files
# TODO: Set up Azure Application Insights for monitoring
