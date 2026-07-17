import os
from pathlib import Path

from dotenv import load_dotenv

# Step 1: Load environment variables from .env file if present
# This populates os.environ with values from the .env file.
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Step 2: Import and call settings_loader.load_settings()
# This ensures all known settings are defined in os.environ,
# applying defaults if necessary, based on what's now in os.environ (after .env load).
# It also returns the resolved_settings dictionary, which base.py will use.
from .settings_loader import load_settings

# This call primarily ensures os.environ is fully populated.
# The returned dictionary is stored if needed, but os.environ is the key.
_resolved_settings_for_base = load_settings()


# Step 3: Now that os.environ is primed, import base settings.
# base.py can now safely access os.environ or use the _resolved_settings_for_base.
from .base import *  # noqa: F401, F403

# Step 4: Get the environment setting and load environment-specific settings.
# These specific settings files can override values set in base.py or directly in os.environ.
environment = os.getenv("DJANGO_SETTINGS_MODULE", "konveyor.settings.development")

if environment == "konveyor.settings.development":
    from .development import *  # noqa: F401, F403
elif environment == "konveyor.settings.production":
    from .production import *  # noqa: F401, F403
elif environment == "konveyor.settings.test":
    from .test import *  # noqa: F401, F403
else:
    raise ImportError(
        f'Settings module "{environment}" not found. Check DJANGO_SETTINGS_MODULE environment variable.'  # noqa: E501
    )

# Expose the resolved settings dictionary at the package level if desired,
# though direct use of os.environ.get() is often cleaner in other modules.
# This makes `azure_settings` available if imported from `konveyor.settings`
azure_settings = _resolved_settings_for_base
