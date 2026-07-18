"""
Document models for LegacyLens.

Stores uploaded document metadata and parsed chunks.
Files are saved to MEDIA_ROOT/documents/ on the local filesystem.
"""

import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models

from legacylens.apps.core.models import TimeStampedModel


def validate_file_extension(value):
    """Validate that uploaded file has an allowed extension."""
    valid_extensions = [".pdf", ".docx", ".md", ".txt"]
    ext = os.path.splitext(value.name)[1]
    if ext.lower() not in valid_extensions:
        raise ValidationError(
            f"Unsupported file type: {ext}. "
            f"Allowed: {', '.join(valid_extensions)}"
        )


class Document(TimeStampedModel):
    """Uploaded document tracked in the system.

    Documents are stored on the local filesystem under
    media/documents/ and their text content is chunked
    and sent to Supermemory for semantic search.
    """

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    title = models.CharField(max_length=255)
    filename = models.CharField(
        max_length=255, null=True, blank=True
    )
    size = models.IntegerField(
        null=True, blank=True, help_text="File size in bytes"
    )
    file_path = models.CharField(
        max_length=512,
        help_text="Path to file on local filesystem",
    )
    content_type = models.CharField(max_length=100)
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("PROCESSING", "Processing"),
            ("PROCESSED", "Processed"),
            ("FAILED", "Failed"),
        ],
        default="PENDING",
    )
    error_message = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Document"
        verbose_name_plural = "Documents"


class DocumentChunk(TimeStampedModel):
    """A parsed chunk of a document.

    Each chunk stores a portion of the document text along
    with its position index for reconstruction.
    """

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks",
    )
    chunk_index = models.IntegerField()
    content = models.TextField(
        blank=True,
        default="",
        help_text="Text content of this chunk",
    )
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return (
            f"{self.document.title} — chunk {self.chunk_index}"
        )

    class Meta:
        ordering = ["document", "chunk_index"]
        verbose_name = "Document Chunk"
        verbose_name_plural = "Document Chunks"
