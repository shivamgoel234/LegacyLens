"""Core app URL configuration — serves web UI pages."""

from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path(
        "knowledge/",
        views.knowledge_graph,
        name="knowledge_graph",
    ),
    path("chat/", views.chat_page, name="chat"),
    path(
        "documents/",
        views.documents_page,
        name="documents",
    ),
    path(
        "employees/",
        views.employees_page,
        name="employees",
    ),
    path("gaps/", views.gaps_page, name="gaps"),
    path(
        "healthz/",
        views.health_check,
        name="health_check",
    ),
]
