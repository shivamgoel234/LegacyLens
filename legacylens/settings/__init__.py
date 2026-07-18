"""
LegacyLens settings package.

Loads .env file, then delegates to the correct environment module
based on DJANGO_SETTINGS_MODULE.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Step 1: Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Step 2: Determine which environment module to load
environment = os.getenv(
    "DJANGO_SETTINGS_MODULE",
    "legacylens.settings.development",
)

# Step 3: Import the appropriate settings module
if environment == "legacylens.settings.development":
    from .development import *  # noqa: F401, F403
elif environment == "legacylens.settings.production":
    from .production import *  # noqa: F401, F403
elif environment == "legacylens.settings.test":
    from .test import *  # noqa: F401, F403
else:
    # Fallback: load development settings
    from .development import *  # noqa: F401, F403
