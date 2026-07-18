"""Document app URL configuration."""

from django.urls import path

from . import views

app_name = "documents"

urlpatterns = [
    path("upload/", views.upload_document, name="upload"),
    path("list/", views.list_documents, name="list"),
    path("<uuid:pk>/delete/", views.delete_document, name="delete"),
]
