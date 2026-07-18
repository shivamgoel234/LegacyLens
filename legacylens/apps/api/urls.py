"""LegacyLens API app URL configuration."""

from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    path("status/", views.llm_status, name="llm_status"),
]
