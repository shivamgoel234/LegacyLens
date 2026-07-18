"""LegacyLens API app views — general status endpoints."""

import os

from django.conf import settings
from django.http import JsonResponse


def llm_status(request):
    """Return the LLM provider configuration status."""
    return JsonResponse(
        {
            "status": "ok",
            "provider": "NVIDIA NIM",
            "base_url": getattr(settings, "OPENAI_BASE_URL", ""),
            "model": getattr(settings, "OPENAI_MODEL", ""),
            "configured": bool(os.environ.get("OPENAI_API_KEY")),
        }
    )
