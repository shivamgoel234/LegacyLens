from django.apps import AppConfig


class KnowledgeConfig(AppConfig):
    """Django app configuration for the LegacyLens Knowledge Graph."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "legacylens.apps.knowledge"
    verbose_name = "LegacyLens Knowledge Graph"
