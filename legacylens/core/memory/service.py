"""MemoryService — high-level facade over Supermemory for LegacyLens.

Every public method delegates to the Supermemory SDK client using the
CORRECT v2 API signatures (verified against supermemory.ai/docs):

    - add():             client.add(content, container_tags, ...)
    - search:            client.search.memories(q, container_tag, ...)
    - file upload:       client.documents.upload_file(file, container_tags)
    - user profile:      client.profile(container_tag)
    - result fields:     item.memory | item.chunk, item.similarity

All methods add organisation-scoped container tags so that multi-tenant
isolation is maintained without any extra infrastructure.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

from legacylens.core.memory.client import get_supermemory_client

logger = logging.getLogger(__name__)


class MemoryService:
    """Organisation-aware memory layer built on Supermemory.

    Attributes:
        org_name: The organisation slug used to namespace all
            stored memories.  Read from the ``LEGACYLENS_ORG_NAME``
            environment variable, defaulting to ``"legacylens_org"``.
    """

    def __init__(self) -> None:
        self.client = get_supermemory_client()
        raw_name: str = os.environ.get(
            "LEGACYLENS_ORG_NAME", "legacylens_org"
        )
        # Supermemory container tags must match ^[a-zA-Z0-9_:-]+$
        import re
        self.org_name: str = re.sub(
            r"[^a-zA-Z0-9_:-]", "_", raw_name
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_results(
        self, results: Any
    ) -> list[dict[str, Any]]:
        """Parse SDK search results into a stable list of dicts.

        The Supermemory SDK returns a SearchResponse object.
        Each item has either a `memory` or `chunk` field (never both),
        and `similarity` (not `score`).

        Args:
            results: Raw SearchResponse from client.search.memories().

        Returns:
            List of dicts with ``content``, ``score``, ``metadata``.
        """
        formatted: list[dict[str, Any]] = []
        for item in getattr(results, "results", []):
            # hybrid search returns memory OR chunk
            content = getattr(item, "memory", None) or getattr(
                item, "chunk", ""
            )
            formatted.append(
                {
                    "content": content,
                    # SDK field is "similarity", not "score"
                    "score": getattr(item, "similarity", 0.0),
                    "metadata": getattr(item, "metadata", {}) or {},
                }
            )
        return formatted

    # ------------------------------------------------------------------
    # Facts
    # ------------------------------------------------------------------

    def store_fact(self, fact: dict[str, Any]) -> dict[str, Any]:
        """Persist a single knowledge fact in Supermemory.

        Args:
            fact: A dictionary that **must** contain at least a
                ``content`` key.  Optional keys include ``category``,
                ``tags``, ``confidence_score``, ``source``,
                ``employee_id``, and ``custom_id``.

        Returns:
            The raw response from the Supermemory ``add`` call.
        """
        container_tags = [
            f"org:{self.org_name}",
            "type:fact",
        ]

        if fact.get("category"):
            container_tags.append(f"category:{fact['category']}")
        if fact.get("employee_id"):
            container_tags.append(
                f"employee:{fact['employee_id']}"
            )

        metadata: dict[str, Any] = {
            "category": fact.get("category", "general"),
            "confidence_score": str(
                fact.get("confidence_score", 0.8)
            ),
            "source": fact.get("source", "unknown"),
            "status": fact.get("status", "active"),
            "tags": json.dumps(fact.get("tags", [])),
            "stored_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            # Correct SDK call: client.add() — NOT client.memories.add()
            result = self.client.add(
                content=fact["content"],
                container_tags=container_tags,
                custom_id=fact.get("custom_id"),
                metadata=metadata,
            )
            logger.info(
                "Stored fact in category '%s' for org '%s'",
                fact.get("category", "general"),
                self.org_name,
            )
            return {"id": getattr(result, "id", ""), "status": "ok"}
        except Exception as exc:
            logger.error(
                "Failed to store fact: %s", exc, exc_info=True
            )
            raise

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search_knowledge(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Hybrid (semantic + keyword) search over stored memories.

        Args:
            query: Natural-language search string.
            filters: Optional filter dict.  Supported keys are
                ``category``, ``employee_id``, and ``status``.
            limit: Maximum number of results to return.

        Returns:
            A list of result dicts, each containing ``content``,
            ``score``, and ``metadata``.
        """
        # Build base container tag for search
        # search.memories() uses singular container_tag, not list
        container_tag = f"org:{self.org_name}"

        # Build metadata filters from filters dict
        metadata_filters = None
        if filters:
            filter_clauses = []
            if filters.get("category"):
                filter_clauses.append(
                    {
                        "key": "category",
                        "value": filters["category"],
                    }
                )
            if filters.get("employee_id"):
                filter_clauses.append(
                    {
                        "key": "employee_id",
                        "value": filters["employee_id"],
                    }
                )
            if filter_clauses:
                metadata_filters = {"AND": filter_clauses}

        try:
            # Correct SDK call: client.search.memories()
            # Parameters: q (not query), container_tag (singular)
            kwargs: dict[str, Any] = {
                "q": query,
                "container_tag": container_tag,
                "search_mode": "hybrid",
                "limit": limit,
            }
            if metadata_filters:
                kwargs["filters"] = metadata_filters

            results = self.client.search.memories(**kwargs)
            return self._parse_results(results)

        except Exception as exc:
            logger.error(
                "Search failed for query '%s': %s",
                query,
                exc,
                exc_info=True,
            )
            return []

    # ------------------------------------------------------------------
    # Employee profiles
    # ------------------------------------------------------------------

    def get_employee_profile(
        self,
        employee_id: str,
        query: str = "",
    ) -> dict[str, Any]:
        """Retrieve a contextual employee profile via Supermemory.

        Uses client.profile() which aggregates all memories
        associated with a given container tag into a profile.

        Args:
            employee_id: Unique employee identifier.
            query: Optional contextual query to focus the profile.

        Returns:
            A dictionary with ``employee_id``, ``static``,
            ``dynamic``, and ``related_facts`` keys.
        """
        container_tag = f"employee:{employee_id}"

        try:
            # Correct SDK call: client.profile(container_tag=...)
            # Returns: profile.profile.static, profile.profile.dynamic
            profile_resp = self.client.profile(
                container_tag=container_tag,
            )
            profile_obj = getattr(profile_resp, "profile", None)
            return {
                "employee_id": employee_id,
                "static": getattr(profile_obj, "static", ""),
                "dynamic": getattr(profile_obj, "dynamic", ""),
                "related_facts": getattr(
                    profile_resp, "related_facts", []
                ),
            }

        except Exception as exc:
            logger.error(
                "Failed to get profile for employee '%s': %s",
                employee_id,
                exc,
                exc_info=True,
            )
            return {
                "employee_id": employee_id,
                "static": "",
                "dynamic": "",
                "related_facts": [],
            }

    # ------------------------------------------------------------------
    # Contradiction detection
    # ------------------------------------------------------------------

    def detect_contradictions(
        self,
        new_fact_content: str,
    ) -> list[dict[str, Any]]:
        """Find existing facts that may contradict *new_fact_content*.

        Performs a high-recall semantic search and returns the
        closest matches so the caller (KnowledgeAgent) can run
        LLM-based contradiction analysis on them.

        Args:
            new_fact_content: The text of the fact to check.

        Returns:
            A list of potentially conflicting fact dicts.
        """
        container_tag = f"org:{self.org_name}"

        try:
            results = self.client.search.memories(
                q=new_fact_content,
                container_tag=container_tag,
                search_mode="hybrid",
                limit=5,
            )

            conflicts: list[dict[str, Any]] = []
            for item in getattr(results, "results", []):
                # SDK field: "similarity" not "score"
                similarity = getattr(item, "similarity", 0.0)
                if similarity > 0.6:
                    content = getattr(
                        item, "memory", None
                    ) or getattr(item, "chunk", "")
                    conflicts.append(
                        {
                            "content": content,
                            "score": similarity,
                            "metadata": getattr(
                                item, "metadata", {}
                            )
                            or {},
                        }
                    )
            return conflicts

        except Exception as exc:
            logger.error(
                "Contradiction detection failed: %s",
                exc,
                exc_info=True,
            )
            return []

    # ------------------------------------------------------------------
    # Conversations
    # ------------------------------------------------------------------

    def store_conversation(
        self,
        employee_id: str,
        role: str,
        content: str,
    ) -> dict[str, Any]:
        """Persist a chat exchange to Supermemory.

        Args:
            employee_id: The employee / session this belongs to.
            role: ``"user"``, ``"assistant"``, or ``"exchange"``.
            content: The message body or full exchange string.

        Returns:
            Dict with id and status.
        """
        container_tags = [
            f"org:{self.org_name}",
            f"employee:{employee_id}",
            "type:conversation",
        ]

        metadata: dict[str, Any] = {
            "role": role,
            "employee_id": employee_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            result = self.client.add(
                content=f"[{role}] {content}",
                container_tags=container_tags,
                metadata=metadata,
            )
            logger.info(
                "Stored %s conversation for employee '%s'",
                role,
                employee_id,
            )
            return {"id": getattr(result, "id", ""), "status": "ok"}

        except Exception as exc:
            logger.error(
                "Failed to store conversation: %s",
                exc,
                exc_info=True,
            )
            raise

    # ------------------------------------------------------------------
    # Documents — text content
    # ------------------------------------------------------------------

    def store_document(
        self,
        title: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        doc_id: str | None = None,
    ) -> dict[str, Any]:
        """Ingest a document as text into Supermemory.

        Use this for text-based documents when you have already
        extracted the text.  For binary files (PDF, DOCX), use
        ``store_file()`` instead — it lets Supermemory handle
        extraction natively.

        Args:
            title: Human-readable document title.
            content: The full document text.
            metadata: Optional extra metadata.
            doc_id: Optional stable ID for deduplication.

        Returns:
            Dict with id and status.
        """
        container_tags = [
            f"org:{self.org_name}",
            "type:document",
        ]

        doc_metadata: dict[str, Any] = {
            "title": title,
            "stored_at": datetime.now(timezone.utc).isoformat(),
        }
        if metadata:
            if metadata.get("department"):
                container_tags.append(
                    f"department:{metadata['department']}"
                )
            # Flatten metadata — Supermemory only accepts scalar values
            for k, v in metadata.items():
                if isinstance(v, (str, int, float, bool)):
                    doc_metadata[k] = v

        try:
            result = self.client.add(
                content=f"Document: {title}\n\n{content}",
                container_tags=container_tags,
                custom_id=f"doc_{doc_id}" if doc_id else None,
                metadata=doc_metadata,
            )
            logger.info(
                "Stored document '%s' for org '%s'",
                title,
                self.org_name,
            )
            return {"id": getattr(result, "id", ""), "status": "ok"}

        except Exception as exc:
            logger.error(
                "Failed to store document '%s': %s",
                title,
                exc,
                exc_info=True,
            )
            raise

    # ------------------------------------------------------------------
    # Documents — native file upload (PDF/DOCX/images)
    # ------------------------------------------------------------------

    def store_file(
        self,
        file_path: str,
        doc_id: str,
        title: str,
    ) -> dict[str, Any]:
        """Upload a binary file directly to Supermemory.

        Supermemory handles text extraction, OCR, chunking, and
        embedding natively.  Supports: PDF, DOC, DOCX, TXT, MD,
        JPG, PNG, CSV.

        Args:
            file_path: Absolute path to the file on disk.
            doc_id: Your stable ID for this document (deduplication).
            title: Human-readable title.

        Returns:
            Dict with id and status from Supermemory.
        """
        container_tags = [
            f"org:{self.org_name}",
            "type:document",
        ]

        try:
            with open(file_path, "rb") as f:
                result = self.client.documents.upload_file(
                    file=f,
                    container_tags=container_tags,
                    custom_id=f"doc_{doc_id}",
                )
            logger.info(
                "Uploaded file '%s' (doc_id=%s) to Supermemory",
                title,
                doc_id,
            )
            return {
                "id": getattr(result, "id", ""),
                "status": getattr(result, "status", "queued"),
            }

        except Exception as exc:
            logger.error(
                "Failed to upload file '%s': %s",
                file_path,
                exc,
                exc_info=True,
            )
            raise

    # ------------------------------------------------------------------
    # Memory stats
    # ------------------------------------------------------------------

    def get_memory_count(self) -> int:
        """Get approximate count of memories for the organisation.

        Performs a broad search and returns the total field from the
        response.  Used for the dashboard stats widget.

        Returns:
            Integer count of memories, or 0 on error.
        """
        try:
            results = self.client.search.memories(
                q="knowledge",
                container_tag=f"org:{self.org_name}",
                search_mode="hybrid",
                limit=1,
            )
            return getattr(results, "total", 0) or 0
        except Exception as exc:
            logger.error(
                "Failed to get memory count: %s", exc
            )
            return 0
