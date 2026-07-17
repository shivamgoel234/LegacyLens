"""
Settings loader utility to ensure environment variables are loaded correctly.
"""

import os


def load_settings():
    """Load environment variables and settings in the correct order.
    This function assumes that load_dotenv has already been called.
    It defines all known settings, applies defaults if not present in os.environ,
    and ensures os.environ is updated with the final resolved values.
    """
    # Define all known settings and their defaults
    # Defaults are used if the variable is not found in os.environ
    defined_settings = {
        # Azure Configuration
        "AZURE_KEY_VAULT_URL": None,
        "AZURE_COGNITIVE_SEARCH_ENDPOINT": None,
        "AZURE_TENANT_ID": None,
        "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT": None,
        "AZURE_DOCUMENT_INTELLIGENCE_API_KEY": None,
        "AZURE_SEARCH_API_KEY": None,
        "AZURE_CLIENT_ID": None,
        "AZURE_CLIENT_SECRET": None,
        "AZURE_OPENAI_API_KEY": None,
        "AZURE_OPENAI_ENDPOINT": None,
        "AZURE_OPENAI_CHAT_DEPLOYMENT": "gpt-4o",  # Default value example
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "text-embedding-ada-002",  # Default value example
        "AZURE_SEARCH_INDEX_NAME": "konveyor-documents",
        "AZURE_OPENAI_API_VERSION": "2024-05-13",  # Default or common value
        "AZURE_STORAGE_CONNECTION_STRING": None,
        "AZURE_STORAGE_CONTAINER_NAME": "documents",  # Default value example
        "AZURE_LOCATION": "eastus",
        "AZURE_SUBSCRIPTION_ID": None,
        # Django Settings
        "DJANGO_ENVIRONMENT": "development",
        "DJANGO_SECRET_KEY": "a_default_fallback_secret_key_if_not_set",  # Ensure a fallback
        "ALLOWED_HOSTS": "localhost,127.0.0.1",
        # Database Settings
        "DB_NAME": "konveyor",
        "DB_USER": "postgres",
        "DB_PASSWORD": "postgres",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        # Bot Framework / Slack
        "MICROSOFT_APP_ID": None,
        "MICROSOFT_APP_PASSWORD": None,
        "SLACK_BOT_TOKEN": None,
        "SLACK_APP_TOKEN": None,
        "SLACK_SIGNING_SECRET": None,
        "SLACK_CLIENT_ID": None,
        "SLACK_CLIENT_SECRET": None,
    }

    resolved_settings = {}
    for key, default_value in defined_settings.items():
        # Get value from os.environ, or use default if not found
        value = os.environ.get(key, default_value)

        # Ensure os.environ is updated with the resolved value
        # (even if it's the default, or if it was already set)
        if value is not None:  # Avoid setting None into os.environ
            os.environ[key] = str(value)  # Ensure it's a string for environ
            resolved_settings[key] = value
        elif (
            key in os.environ
        ):  # If it was explicitly set to empty string, respect that for resolved_settings
            resolved_settings[key] = os.environ[key]

    return resolved_settings
