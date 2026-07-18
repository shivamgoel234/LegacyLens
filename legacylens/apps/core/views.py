"""
Core app views — serves web UI pages and health check.

These views render Django templates for the LegacyLens web interface.
"""

import logging

from django.http import JsonResponse
from django.shortcuts import render

logger = logging.getLogger(__name__)


def dashboard(request):
    """Render the main dashboard with summary counts."""
    from legacylens.apps.documents.models import Document
    from legacylens.apps.knowledge.models import (
        Employee,
        KnowledgeFact,
        KnowledgeGap,
    )

    context = {
        "fact_count": KnowledgeFact.objects.count(),
        "gap_count": KnowledgeGap.objects.count(),
        "employee_count": Employee.objects.count(),
        "document_count": Document.objects.count(),
        "recent_facts": KnowledgeFact.objects.order_by("-created_at")[:10],
    }
    return render(request, "dashboard.html", context)


def knowledge_graph(request):
    """Render the interactive knowledge graph page."""
    return render(request, "knowledge_graph.html")


def chat_page(request):
    """Render the chat interface page."""
    return render(request, "chat.html")


def documents_page(request):
    """Render the documents management page."""
    from legacylens.apps.documents.models import Document

    context = {
        "documents": Document.objects.all().order_by(
            "-created_at"
        ),
    }
    return render(request, "documents.html", context)


def employees_page(request):
    """Render the employees page."""
    from legacylens.apps.knowledge.models import Employee

    context = {
        "employees": Employee.objects.all().order_by("name"),
    }
    return render(request, "employees.html", context)


def gaps_page(request):
    """Render the knowledge gaps page."""
    from legacylens.apps.knowledge.models import KnowledgeGap

    context = {
        "gaps": KnowledgeGap.objects.all().order_by(
            "-created_at"
        ),
    }
    return render(request, "gaps.html", context)


def health_check(request):
    """Health check endpoint for LegacyLens.

    Checks database connectivity and Supermemory Local status via the
    official SDK.  Returns memory count for the dashboard stats widget.

    Always returns HTTP 200 to keep the app running even when
    downstream services are degraded.
    """
    import os

    from django.db import connection

    health: dict = {
        "status": "healthy",
        "database": "unknown",
        "supermemory": {
            "status": "unknown",
            "url": os.environ.get(
                "SUPERMEMORY_BASE_URL", "http://localhost:6767"
            ),
            "memory_count": 0,
        },
    }

    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health["database"] = "connected"
    except Exception as exc:
        logger.error("Database health check failed: %s", exc)
        health["database"] = "error"
        health["status"] = "degraded"

    # Check Supermemory Local via SDK — not raw HTTP requests
    try:
        from legacylens.core.memory.service import MemoryService

        mem = MemoryService()
        memory_count = mem.get_memory_count()
        health["supermemory"]["status"] = "connected"
        health["supermemory"]["memory_count"] = memory_count
    except Exception as exc:
        logger.warning(
            "Supermemory health check failed: %s", exc
        )
    return JsonResponse(health)
