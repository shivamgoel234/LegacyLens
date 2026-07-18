"""DRF serializers for the LegacyLens Knowledge Graph models."""

from rest_framework import serializers

from legacylens.apps.knowledge.models import (
    Employee,
    KnowledgeFact,
    KnowledgeGap,
    KnowledgeRelationship,
    OnboardingPlan,
)


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for :class:`Employee`.

    Includes a computed ``fact_count`` showing how many
    KnowledgeFact records are attributed to this employee.
    """

    fact_count = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "id",
            "name",
            "email",
            "role",
            "department",
            "expertise_areas",
            "status",
            "supermemory_container",
            "departure_date",
            "fact_count",
            "created_at",
            "modified_at",
        ]
        read_only_fields = [
            "id",
            "supermemory_container",
            "created_at",
            "modified_at",
        ]

    def get_fact_count(self, obj: Employee) -> int:
        """Return number of facts contributed by employee."""
        return obj.contributed_facts.count()


class EmployeeMinimalSerializer(serializers.ModelSerializer):
    """Lightweight employee serializer for nested use."""

    class Meta:
        model = Employee
        fields = ["id", "name", "role", "department"]


class KnowledgeFactSerializer(serializers.ModelSerializer):
    """Serializer for :class:`KnowledgeFact`.

    Includes a nested read-only representation of the
    source employee for display purposes.
    """

    source_employee = EmployeeMinimalSerializer(
        read_only=True,
    )
    source_employee_id = serializers.UUIDField(
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = KnowledgeFact
        fields = [
            "id",
            "content",
            "summary",
            "category",
            "status",
            "confidence_score",
            "source_employee",
            "source_employee_id",
            "source_document",
            "source_type",
            "supersedes",
            "valid_from",
            "valid_until",
            "supermemory_doc_id",
            "tags",
            "metadata",
            "created_at",
            "modified_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "modified_at",
        ]

    def create(self, validated_data):
        """Handle source_employee_id → source_employee FK."""
        employee_id = validated_data.pop(
            "source_employee_id", None
        )
        if employee_id:
            validated_data["source_employee_id"] = (
                employee_id
            )
        return super().create(validated_data)


class KnowledgeRelationshipSerializer(
    serializers.ModelSerializer,
):
    """Serializer for :class:`KnowledgeRelationship`."""

    class Meta:
        model = KnowledgeRelationship
        fields = [
            "id",
            "source",
            "target",
            "relationship_type",
            "similarity_score",
            "is_confirmed",
            "metadata",
            "created_at",
            "modified_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "modified_at",
        ]


class KnowledgeGapSerializer(serializers.ModelSerializer):
    """Serializer for :class:`KnowledgeGap`."""

    class Meta:
        model = KnowledgeGap
        fields = [
            "id",
            "title",
            "description",
            "severity",
            "status",
            "related_facts",
            "assigned_employee",
            "suggested_question",
            "answer",
            "created_at",
            "modified_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "modified_at",
        ]


class OnboardingPlanSerializer(
    serializers.ModelSerializer,
):
    """Serializer for :class:`OnboardingPlan`."""

    class Meta:
        model = OnboardingPlan
        fields = [
            "id",
            "employee",
            "title",
            "role_focus",
            "plan_data",
            "progress",
            "is_active",
            "created_at",
            "modified_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "modified_at",
        ]
