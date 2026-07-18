"""Django models for the LegacyLens Knowledge Graph.

Defines the five core domain models: Employee, KnowledgeFact,
KnowledgeRelationship, KnowledgeGap, and OnboardingPlan.
"""

import uuid

from django.conf import settings
from django.db import models

from legacylens.apps.core.models import TimeStampedModel


# ------------------------------------------------------------------
# Choices
# ------------------------------------------------------------------

EMPLOYEE_STATUS_CHOICES = [
    ("active", "Active"),
    ("departing", "Departing"),
    ("departed", "Departed"),
    ("onboarding", "Onboarding"),
]

FACT_CATEGORY_CHOICES = [
    ("architecture", "Architecture"),
    ("process", "Process"),
    ("tooling", "Tooling"),
    ("domain", "Domain"),
    ("decision", "Decision"),
    ("ownership", "Ownership"),
    ("onboarding", "Onboarding"),
    ("tribal", "Tribal Knowledge"),
]

FACT_STATUS_CHOICES = [
    ("current", "Current"),
    ("historical", "Historical"),
    ("deprecated", "Deprecated"),
    ("undocumented", "Undocumented"),
    ("conflicting", "Conflicting"),
    ("unverified", "Unverified"),
]

SOURCE_TYPE_CHOICES = [
    ("interview", "Interview"),
    ("document", "Document"),
    ("code", "Code"),
    ("inferred", "Inferred"),
    ("manual", "Manual"),
]

RELATIONSHIP_TYPE_CHOICES = [
    ("supersedes", "Supersedes"),
    ("related", "Related"),
    ("depends_on", "Depends On"),
    ("contradicts", "Contradicts"),
    ("derived_from", "Derived From"),
    ("owned_by", "Owned By"),
]

GAP_SEVERITY_CHOICES = [
    ("critical", "Critical"),
    ("high", "High"),
    ("medium", "Medium"),
    ("low", "Low"),
]

GAP_STATUS_CHOICES = [
    ("detected", "Detected"),
    ("asked", "Asked"),
    ("answered", "Answered"),
    ("resolved", "Resolved"),
    ("wont_fix", "Won't Fix"),
]


# ------------------------------------------------------------------
# Models
# ------------------------------------------------------------------


class Employee(TimeStampedModel):
    """An organisational employee tracked by LegacyLens.

    Attributes:
        supermemory_container: Auto-set on first save to
            ``employee_{self.id}`` for Supermemory scoping.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_profile",
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    role = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    expertise_areas = models.JSONField(default=list)
    status = models.CharField(
        max_length=20,
        choices=EMPLOYEE_STATUS_CHOICES,
        default="active",
    )
    supermemory_container = models.CharField(
        max_length=100, blank=True
    )
    departure_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    def __str__(self) -> str:
        return f"{self.name} ({self.status})"

    def save(self, *args, **kwargs):
        """Auto-populate supermemory_container on first save."""
        if not self.supermemory_container:
            if not self.id:
                self.id = uuid.uuid4()
            self.supermemory_container = (
                f"employee_{self.id}"
            )
        super().save(*args, **kwargs)


class KnowledgeFact(TimeStampedModel):
    """A single unit of organisational knowledge.

    Facts are the atomic building blocks of the LegacyLens
    knowledge graph.  Each fact has a category, a confidence
    score, and provenance tracking.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    content = models.TextField()
    summary = models.CharField(max_length=500, blank=True)
    category = models.CharField(
        max_length=100,
        choices=FACT_CATEGORY_CHOICES,
    )
    status = models.CharField(
        max_length=20,
        choices=FACT_STATUS_CHOICES,
        default="current",
    )
    confidence_score = models.FloatField(default=0.5)
    source_employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contributed_facts",
    )
    source_document = models.ForeignKey(
        "legacylens_documents.Document",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="extracted_facts",
    )
    source_type = models.CharField(
        max_length=50,
        choices=SOURCE_TYPE_CHOICES,
    )
    supersedes = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="superseded_by",
    )
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    supermemory_doc_id = models.CharField(
        max_length=100, blank=True
    )
    tags = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Knowledge Fact"
        verbose_name_plural = "Knowledge Facts"
        indexes = [
            models.Index(
                fields=["category", "status"],
                name="idx_fact_category_status",
            ),
            models.Index(
                fields=["source_employee"],
                name="idx_fact_source_employee",
            ),
            models.Index(
                fields=["confidence_score"],
                name="idx_fact_confidence",
            ),
        ]

    def __str__(self) -> str:
        label = self.summary or self.content[:80]
        return f"[{self.category}] {label}"


class KnowledgeRelationship(TimeStampedModel):
    """A directed edge between two KnowledgeFact nodes.

    Used to build the knowledge graph that powers the D3.js
    visualisation and the contradiction / dependency analysis.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    source = models.ForeignKey(
        KnowledgeFact,
        on_delete=models.CASCADE,
        related_name="outgoing_relationships",
    )
    target = models.ForeignKey(
        KnowledgeFact,
        on_delete=models.CASCADE,
        related_name="incoming_relationships",
    )
    relationship_type = models.CharField(
        max_length=30,
        choices=RELATIONSHIP_TYPE_CHOICES,
    )
    similarity_score = models.FloatField(default=0.0)
    is_confirmed = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [
            ("source", "target", "relationship_type"),
        ]
        verbose_name = "Knowledge Relationship"
        verbose_name_plural = "Knowledge Relationships"

    def __str__(self) -> str:
        return (
            f"{self.source_id} "
            f"—[{self.relationship_type}]→ "
            f"{self.target_id}"
        )


class KnowledgeGap(TimeStampedModel):
    """A detected gap in organisational knowledge.

    Gaps can be auto-detected by the KnowledgeAgent or
    created manually by users.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(
        max_length=20,
        choices=GAP_SEVERITY_CHOICES,
    )
    status = models.CharField(
        max_length=20,
        choices=GAP_STATUS_CHOICES,
        default="detected",
    )
    related_facts = models.ManyToManyField(
        KnowledgeFact,
        blank=True,
        related_name="related_gaps",
    )
    assigned_employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_gaps",
    )
    suggested_question = models.TextField(blank=True)
    answer = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Knowledge Gap"
        verbose_name_plural = "Knowledge Gaps"

    def __str__(self) -> str:
        return f"[{self.severity}] {self.title}"


class OnboardingPlan(TimeStampedModel):
    """A personalised onboarding plan for a new employee.

    Generated by the KnowledgeAgent based on the employee's
    role and available organisational knowledge.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="onboarding_plans",
    )
    title = models.CharField(max_length=255)
    role_focus = models.CharField(
        max_length=255, blank=True
    )
    plan_data = models.JSONField(default=dict)
    progress = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Onboarding Plan"
        verbose_name_plural = "Onboarding Plans"

    def __str__(self) -> str:
        return f"{self.title} — {self.employee.name}"
