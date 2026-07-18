"""
Document views for LegacyLens.

Handles file upload (saves to media/documents/, then sends to
Supermemory Local for native processing) and listing.
"""

import logging
import os

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from legacylens.apps.documents.models import Document

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def upload_document(request):
    """Accept a file via POST, save to disk, forward to Supermemory.

    Workflow:
        1. Validate file extension.
        2. Save file to ``media/documents/``.
        3. Create ``Document`` DB record (status=PENDING).
        4. Upload file to Supermemory Local via native SDK upload
           (Supermemory handles OCR / text extraction itself).
        5. Update DB record with Supermemory document ID.

    Returns JSON with the document ID and Supermemory status.
    """
    if "file" not in request.FILES:
        return JsonResponse(
            {
                "status": "error",
                "message": "No file provided",
                "code": "MISSING_FILE",
            },
            status=400,
        )

    uploaded_file = request.FILES["file"]
    filename = uploaded_file.name
    content_type = (
        uploaded_file.content_type or "application/octet-stream"
    )

    # Validate extension
    allowed = getattr(
        settings,
        "LEGACYLENS_ALLOWED_UPLOAD_EXTENSIONS",
        [".pdf", ".docx", ".doc", ".txt", ".md", ".csv"],
    )
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed:
        return JsonResponse(
            {
                "status": "error",
                "message": (
                    f"Unsupported file type: {ext}. "
                    f"Allowed: {', '.join(allowed)}"
                ),
                "code": "INVALID_EXTENSION",
            },
            status=400,
        )

    # Ensure upload directory exists
    upload_dir = os.path.join(
        str(settings.MEDIA_ROOT), "documents"
    )
    os.makedirs(upload_dir, exist_ok=True)

    # Save file to disk
    file_path = os.path.join(upload_dir, filename)
    try:
        with open(file_path, "wb+") as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)
    except OSError as exc:
        logger.error("Failed to save file %s: %s", filename, exc)
        return JsonResponse(
            {
                "status": "error",
                "message": "Failed to save file",
                "code": "SAVE_ERROR",
            },
            status=500,
        )

    # Create Document DB record (status=PENDING)
    doc = Document.objects.create(
        title=os.path.splitext(filename)[0],
        filename=filename,
        size=uploaded_file.size,
        file_path=file_path,
        content_type=content_type,
        status="PENDING",
    )

    logger.info(
        "Document saved to disk: %s (id=%s, size=%d)",
        filename,
        doc.id,
        uploaded_file.size,
    )

    # --- SUPERMEMORY INTEGRATION ---
    sm_doc_id = None
    sm_status = "not_sent"
    try:
        from legacylens.core.memory.service import MemoryService

        mem = MemoryService()

        # For text-based files, read content and use store_document
        # (more reliable than binary file upload for .md/.txt)
        text_extensions = {".md", ".txt", ".csv"}
        if ext in text_extensions:
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
            result = mem.store_document(
                title=doc.title,
                content=file_content,
                doc_id=str(doc.id),
            )
        else:
            # Binary files (PDF, DOCX) use native file upload
            result = mem.store_file(
                file_path=file_path,
                doc_id=str(doc.id),
                title=doc.title,
            )

        sm_doc_id = result.get("id", "")
        sm_status = result.get("status", "queued")

        doc.status = "INDEXED"
        doc.save(update_fields=["status"])

        logger.info(
            "Document '%s' sent to Supermemory: id=%s status=%s",
            doc.title,
            sm_doc_id,
            sm_status,
        )

    except Exception as exc:
        logger.error(
            "Supermemory upload failed for doc %s: %s",
            doc.id,
            exc,
            exc_info=True,
        )
        sm_status = f"error: {str(exc)[:100]}"
        doc.status = "ERROR"
        doc.save(update_fields=["status"])

    return JsonResponse(
        {
            "status": "ok",
            "data": {
                "id": str(doc.id),
                "title": doc.title,
                "filename": doc.filename,
                "size": doc.size,
                "status": doc.status,
                "supermemory": {
                    "id": sm_doc_id,
                    "status": sm_status,
                },
            },
        },
        status=201,
    )


@require_http_methods(["GET"])
def list_documents(request):
    """Return a JSON list of all documents."""
    documents = Document.objects.all().order_by("-created_at")
    data = [
        {
            "id": str(doc.id),
            "title": doc.title,
            "filename": doc.filename,
            "size": doc.size,
            "content_type": doc.content_type,
            "status": doc.status,
            "created_at": doc.created_at.isoformat(),
        }
        for doc in documents
    ]
    return JsonResponse({"status": "ok", "data": data})


@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def delete_document(request, pk):
    """Delete a document by primary key.

    Removes the DB record and the file from disk.
    """
    try:
        doc = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Document not found"},
            status=404,
        )

    # Delete file from disk
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except OSError as exc:
            logger.warning(
                "Could not delete file %s: %s",
                doc.file_path,
                exc,
            )

    title = doc.title
    doc.delete()
    logger.info("Document deleted: %s (id=%s)", title, pk)

    return JsonResponse(
        {"status": "ok", "message": f"Document '{title}' deleted"}
    )
