import os  # noqa: F401

from django.core.exceptions import ImproperlyConfigured  # noqa: F401

from .base import *  # noqa: F403, F401
from .base import LOGGING  # Import the base LOGGING dict

DEBUG = False


# Allow localhost for local runs; read extra hosts from env when deployed
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Use in-memory SQLite for faster tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(
            BASE_DIR / "db.sqlite3.test"  # noqa: F405
        ),  # Convert Path to string  # noqa: E501
    }
}

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Test Logging Configuration (modifies base LOGGING)
# Set console to DEBUG for Azure App Service log capture
LOGGING["handlers"]["console"]["level"] = "DEBUG"
LOGGING["loggers"]["django"]["level"] = (
    "DEBUG"  # More verbose Django logs for test debugging
)
LOGGING["loggers"]["legacylens"]["level"] = "DEBUG"
LOGGING["root"]["level"] = "DEBUG"

# Optional: Add a test-specific file handler if needed for local test execution,
# but console is primary for Azure.
if "test_file" not in LOGGING["handlers"]:
    LOGGING["handlers"]["test_file"] = {
        "level": "DEBUG",
        "class": "logging.FileHandler",
        "filename": os.path.join(BASE_DIR, "logs", "legacylens-test.log"),  # noqa: F405
        "formatter": "structured",  # Assumes 'structured' formatter is in base
    }

# Example: If you want legacylens logs to also go to test_file locally
# Ensure the handler is added to the list if not already present
if "test_file" not in LOGGING["loggers"]["legacylens"]["handlers"]:
    LOGGING["loggers"]["legacylens"]["handlers"].append("test_file")
# Ensure root also logs to test_file if desired for local test runs
if "test_file" not in LOGGING["root"]["handlers"]:
    LOGGING["root"]["handlers"].append("test_file")

# Set default mock values for Azure settings in os.environ if not already provided.
# This ensures that tests running in CI or locally without full .env setup
# use predictable mock endpoints.
# These will be picked up by settings_loader.py when it populates os.environ.

MOCK_VALUES = {
    "AZURE_COGNITIVE_SEARCH_ENDPOINT": "https://mock-search-endpoint.search.windows.net",
    "AZURE_SEARCH_API_KEY": "mock-search-api-key",
    "AZURE_OPENAI_ENDPOINT": "https://mock-openai-endpoint.openai.azure.com",
    "AZURE_OPENAI_API_KEY": "mock-openai-api-key",
    "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT": "https://mock-docintel-endpoint.cognitiveservices.azure.com",
    "AZURE_DOCUMENT_INTELLIGENCE_API_KEY": "mock-docintel-api-key",
    "AZURE_STORAGE_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=mockstorageaccount;AccountKey=mockAccountKey;EndpointSuffix=core.windows.net",
    # Add other essential Azure services that need mocking for tests
}

for key, mock_value in MOCK_VALUES.items():
    if not os.environ.get(key):  # Only set if not already present in environment
        os.environ[key] = mock_value

# After os.environ is potentially updated with mock values,
# settings_loader.load_settings() (called via __init__.py and then base.py)
# will use these values if real ones weren't provided.

# The global assignments below are less critical now that os.environ is the primary source,
# but they don't hurt as long as they reflect what's in os.environ.
# However, it's better to rely on settings being loaded consistently via azure_settings or os.environ.

# If specific test logic still relies on these global module variables, ensure they are updated:
if not AZURE_COGNITIVE_SEARCH_ENDPOINT:  # noqa: F405 # This references the global from base.py
    # This direct assignment might be too late or conflict if base.py already tried to set it from a None os.environ value
    # It's better to ensure os.environ was set correctly before base.py runs.
    # The loop above handles os.environ. The `azure_settings` object in `base.py` will reflect this.
    pass  # The logic above should handle this by setting os.environ


if not AZURE_SEARCH_API_KEY:  # noqa: F405
    pass


# Just validate critical settings
def validate_settings():
    # For CI/CD, we don't require real Azure credentials
    # The tests that need real credentials should be skipped if not available
    pass


validate_settings()

# TODO: Configure test-specific settings for mocking Azure services
