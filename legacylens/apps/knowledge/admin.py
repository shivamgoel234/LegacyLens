"""Django admin configuration for the Knowledge app."""

from django.contrib import admin

from legacylens.apps.knowledge.models import (
    Employee,
    KnowledgeFact,
    KnowledgeGap,
    KnowledgeRelationship,
    OnboardingPlan,
)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin view for :class:`Employee`."""

    list_display = [
        "name",
        "email",
        "role",
        "department",
        "status",
        "departure_date",
        "created_at",
    ]
    list_filter = ["status", "department"]
    search_fields = ["name", "email", "role", "department"]


@admin.register(KnowledgeFact)
class KnowledgeFactAdmin(admin.ModelAdmin):
    """Admin view for :class:`KnowledgeFact`."""

    list_display = [
        "summary_or_content",
        "category",
        "status",
        "confidence_score",
        "source_type",
        "source_employee",
        "created_at",
    ]
    list_filter = [
        "category",
        "status",
        "source_type",
        "confidence_score",
    ]
    search_fields = ["content", "summary", "tags"]

    @admin.display(description="Fact")
    def summary_or_content(self, obj):
        """Return summary if available, else truncated content."""
        return obj.summary or obj.content[:80]


@admin.register(KnowledgeRelationship)
class KnowledgeRelationshipAdmin(admin.ModelAdmin):
    """Admin view for :class:`KnowledgeRelationship`."""

    list_display = [
        "source",
        "relationship_type",
        "target",
        "similarity_score",
        "is_confirmed",
        "created_at",
    ]
    list_filter = [
        "relationship_type",
        "is_confirmed",
    ]
    search_fields = [
        "source__content",
        "target__content",
    ]


@admin.register(KnowledgeGap)
class KnowledgeGapAdmin(admin.ModelAdmin):
    """Admin view for :class:`KnowledgeGap`."""

    list_display = [
        "title",
        "severity",
        "status",
        "assigned_employee",
        "created_at",
    ]
    list_filter = ["severity", "status"]
    search_fields = [
        "title",
        "description",
        "suggested_question",
    ]


@admin.register(OnboardingPlan)
class OnboardingPlanAdmin(admin.ModelAdmin):
    """Admin view for :class:`OnboardingPlan`."""

    list_display = [
        "title",
        "employee",
        "role_focus",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active"]
    search_fields = ["title", "role_focus"]
