"""Supermemory Local singleton client for LegacyLens.

Provides a lazily-initialized, process-wide Supermemory client
that reads connection details from environment variables.
"""

import logging
import os

from supermemory import Supermemory

logger = logging.getLogger(__name__)

_client = None


def get_supermemory_client() -> Supermemory:
    """Return a singleton Supermemory client instance.

    The client is created on first call and reused thereafter.
    Connection details are read from environment variables:
        SUPERMEMORY_API_KEY  – defaults to ``sm_local``
        SUPERMEMORY_BASE_URL – defaults to ``http://localhost:6767``

    Returns:
        Supermemory: The shared client instance.
    """
    global _client
    if _client is None:
        base_url = os.environ.get(
            "SUPERMEMORY_BASE_URL", "http://localhost:6767"
        )
        api_key = os.environ.get("SUPERMEMORY_API_KEY", "sm_local")
        _client = Supermemory(
            api_key=api_key,
            base_url=base_url,
        )
        # Use env var directly — avoids accessing private SDK attributes
        logger.info(
            "Supermemory client initialized at %s", base_url
        )
    return _client
