import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-_96kwk)pw9hoq$t6@#4fi!id_8s0*l%l3y0t^8t88^guo)n5%7",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*", "localhost", "127.0.0.1"]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Local apps - use full paths
    "konveyor.apps.core.apps.CoreConfig",
    "konveyor.apps.users.apps.UsersConfig",
    "konveyor.apps.api.apps.ApiConfig",
    "konveyor.apps.documents.apps.DocumentsConfig",
    "konveyor.apps.search.apps.SearchConfig",
    "konveyor.apps.bot.apps.BotConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "konveyor.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "konveyor.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "konveyor"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "postgres"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Media files configuration
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Logging configuration
LOGGING_FORMATTERS = {
    "verbose": {
        "format": "{levelname} {asctime} {module} {message}",
        "style": "{",
    },
    "structured": {
        "format": "{levelname} {asctime} {name} {module} {message}",
        "style": "{",
    },
}

LOGGING_HANDLERS = {
    "console_base": {  # A base console handler
        "class": "logging.StreamHandler",
        "formatter": "structured",  # Assumes 'structured' is in LOGGING_FORMATTERS
    },
    # TODO: Base file handler can be defined here if needed, or in specific environments
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": LOGGING_FORMATTERS,
    "handlers": {
        "console": {
            **LOGGING_HANDLERS["console_base"],  # Spread the base console config
            "level": "INFO",  # Default level for console in base
        }
        # TODO Other base handlers like a base file handler could be added here
        # "file_base": { ... }
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "konveyor": {  # Base for all 'konveyor.*' loggers
            "handlers": ["console"],
            "level": "INFO",  # Default for konveyor apps, overridden in dev/test
            "propagate": True,
        },
        # Specific konveyor sub-modules can be configured here if needed globally
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",  # Default for other libraries
    },
}

# Load all Azure settings - os.environ is already populated by __init__.py via settings_loader

# Core Azure Settings (common across all environments)
AZURE_CORE_SETTINGS = {
    "AZURE_LOCATION": os.getenv("AZURE_LOCATION", "eastus"),
    "AZURE_TENANT_ID": os.getenv("AZURE_TENANT_ID"),
    "AZURE_SUBSCRIPTION_ID": os.getenv("AZURE_SUBSCRIPTION_ID"),
}

# Azure Search Settings - using os.environ.get() directly
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "konveyor-documents")

# For backward compatibility and clarity, set both names
AZURE_COGNITIVE_SEARCH_ENDPOINT = AZURE_SEARCH_ENDPOINT

# Azure Service Configuration - using os.environ.get() directly
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-13")

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "documents")

AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
AZURE_DOCUMENT_INTELLIGENCE_API_KEY = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_API_KEY")

# Slack Integration Settings
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET", "")
