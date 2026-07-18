"""
This service layer file is intentionally left minimal.

The core document processing logic (parsing, chunking, storage)
resides in the framework-agnostic service:
legacylens.core.documents.document_service.DocumentService

The Django-specific integration and model handling is done in:
legacylens.apps.documents.services.document_adapter.DjangoDocumentService
"""

import logging

logger = logging.getLogger(__name__)

# No service class defined here anymore.
# See legacylens.core.documents.document_service for implementation.

logger.info("App-layer document service module loaded (logic resides in core).")
