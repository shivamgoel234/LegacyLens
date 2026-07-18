"""
LegacyLens — Root URL configuration.

Routes requests to the appropriate app-level URL modules.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/knowledge/",
        include("legacylens.apps.knowledge.urls"),
    ),
    path(
        "api/documents/",
        include("legacylens.apps.documents.urls"),
    ),
    path("api/", include("legacylens.apps.api.urls")),
    path("", include("legacylens.apps.core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
