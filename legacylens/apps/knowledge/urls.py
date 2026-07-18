"""URL configuration for the LegacyLens Knowledge app."""

from django.urls import path

from legacylens.apps.knowledge import views

app_name = "knowledge"

urlpatterns = [
    # Facts
    path(
        "facts/",
        views.FactListCreateView.as_view(),
        name="fact-list-create",
    ),
    path(
        "facts/<uuid:pk>/",
        views.FactDetailView.as_view(),
        name="fact-detail",
    ),
    # Knowledge Graph
    path(
        "graph/data/",
        views.KnowledgeGraphDataView.as_view(),
        name="graph-data",
    ),
    # Search
    path(
        "search/",
        views.KnowledgeSearchView.as_view(),
        name="search",
    ),
    # Gaps
    path(
        "gaps/",
        views.KnowledgeGapListView.as_view(),
        name="gap-list",
    ),
    path(
        "gaps/<uuid:pk>/resolve/",
        views.ResolveGapView.as_view(),
        name="gap-resolve",
    ),
    # Employees
    path(
        "employees/",
        views.EmployeeListCreateView.as_view(),
        name="employee-list-create",
    ),
    path(
        "employees/<uuid:pk>/",
        views.EmployeeDetailView.as_view(),
        name="employee-detail",
    ),
    path(
        "employees/<uuid:pk>/profile/",
        views.EmployeeProfileView.as_view(),
        name="employee-profile",
    ),
    path(
        "employees/<uuid:pk>/interview/",
        views.InterviewView.as_view(),
        name="employee-interview",
    ),
    # Agent endpoints
    path(
        "agent/chat/",
        views.AgentChatView.as_view(),
        name="agent-chat",
    ),
    path(
        "agent/extract/",
        views.ExtractFactsView.as_view(),
        name="agent-extract",
    ),
    path(
        "agent/gaps/detect/",
        views.DetectGapsView.as_view(),
        name="agent-detect-gaps",
    ),
    path(
        "agent/onboarding/",
        views.GenerateOnboardingView.as_view(),
        name="agent-onboarding",
    ),
]
