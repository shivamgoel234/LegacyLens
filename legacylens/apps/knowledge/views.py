"""REST API views for the LegacyLens Knowledge app.

All endpoints return ``{status, data}`` on success or
``{status, message}`` on error, per AGENT.md conventions.
"""

import json
import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status as http_status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from legacylens.apps.knowledge.models import (
    Employee,
    KnowledgeFact,
    KnowledgeGap,
    KnowledgeRelationship,
    OnboardingPlan,
)
from legacylens.apps.knowledge.serializers import (
    EmployeeSerializer,
    KnowledgeFactSerializer,
    KnowledgeGapSerializer,
    OnboardingPlanSerializer,
)

logger = logging.getLogger(__name__)


def _error(msg: str, code: int = 400) -> Response:
    """Return a standardised error response."""
    return Response(
        {"status": "error", "message": msg},
        status=code,
    )


def _ok(data=None, code: int = 200) -> Response:
    """Return a standardised success response."""
    return Response(
        {"status": "ok", "data": data},
        status=code,
    )


def _get_memory_service():
    """Lazy-import MemoryService to avoid startup errors."""
    from legacylens.core.memory.service import (
        MemoryService,
    )

    return MemoryService()


def _get_knowledge_agent():
    """Lazy-import KnowledgeAgent."""
    from legacylens.core.agent.knowledge_agent import (
        KnowledgeAgent,
    )

    return KnowledgeAgent()


# ------------------------------------------------------------------
# Fact endpoints
# ------------------------------------------------------------------


@method_decorator(csrf_exempt, name="dispatch")
class FactListCreateView(APIView):
    """GET: list all facts.  POST: create a new fact."""

    def get(self, request: Request) -> Response:
        """Return all facts ordered by newest first."""
        facts = KnowledgeFact.objects.select_related(
            "source_employee",
        ).order_by("-created_at")
        serializer = KnowledgeFactSerializer(
            facts, many=True
        )
        return _ok(serializer.data)

    def post(self, request: Request) -> Response:
        """Create a fact and store it in Supermemory."""
        serializer = KnowledgeFactSerializer(
            data=request.data
        )
        if not serializer.is_valid():
            return _error(
                json.dumps(serializer.errors),
                http_status.HTTP_400_BAD_REQUEST,
            )

        fact = serializer.save()

        try:
            mem = _get_memory_service()
            mem.store_fact(
                {
                    "content": fact.content,
                    "category": fact.category,
                    "confidence_score": fact.confidence_score,
                    "source": fact.source_type,
                    "tags": fact.tags,
                    "employee_id": (
                        str(fact.source_employee_id)
                        if fact.source_employee_id
                        else None
                    ),
                }
            )
        except Exception as exc:
            logger.error(
                "Supermemory store failed for fact "
                "%s: %s",
                fact.id,
                exc,
                exc_info=True,
            )

        return _ok(
            KnowledgeFactSerializer(fact).data,
            http_status.HTTP_201_CREATED,
        )


@method_decorator(csrf_exempt, name="dispatch")
class FactDetailView(APIView):
    """GET / PUT / DELETE a single KnowledgeFact."""

    def get(self, request: Request, pk) -> Response:
        """Return a single fact by primary key."""
        try:
            fact = KnowledgeFact.objects.select_related(
                "source_employee",
            ).get(pk=pk)
        except KnowledgeFact.DoesNotExist:
            return _error("Fact not found", 404)
        return _ok(KnowledgeFactSerializer(fact).data)

    def put(self, request: Request, pk) -> Response:
        """Update a fact."""
        try:
            fact = KnowledgeFact.objects.get(pk=pk)
        except KnowledgeFact.DoesNotExist:
            return _error("Fact not found", 404)

        serializer = KnowledgeFactSerializer(
            fact, data=request.data, partial=True
        )
        if not serializer.is_valid():
            return _error(json.dumps(serializer.errors))
        serializer.save()
        return _ok(serializer.data)

    def delete(self, request: Request, pk) -> Response:
        """Delete a fact."""
        try:
            fact = KnowledgeFact.objects.get(pk=pk)
        except KnowledgeFact.DoesNotExist:
            return _error("Fact not found", 404)
        fact.delete()
        return _ok({"deleted": str(pk)})


# ------------------------------------------------------------------
# Knowledge Graph
# ------------------------------------------------------------------


@method_decorator(csrf_exempt, name="dispatch")
class KnowledgeGraphDataView(APIView):
    """GET: return graph data for D3.js visualisation."""

    def get(self, request: Request) -> Response:
        """Build nodes + edges payload for the graph."""
        facts = KnowledgeFact.objects.all()
        nodes = [
            {
                "id": str(f.id),
                "label": f.summary or f.content[:60],
                "category": f.category,
                "status": f.status,
                "confidence": f.confidence_score,
            }
            for f in facts
        ]

        rels = KnowledgeRelationship.objects.all()
        edges = [
            {
                "source": str(r.source_id),
                "target": str(r.target_id),
                "type": r.relationship_type,
            }
            for r in rels
        ]

        return _ok({"nodes": nodes, "edges": edges})


# ------------------------------------------------------------------
# Search
# ------------------------------------------------------------------


@method_decorator(csrf_exempt, name="dispatch")
class KnowledgeSearchView(APIView):
    """POST {query}: search Supermemory via MemoryService."""

    def post(self, request: Request) -> Response:
        """Run hybrid search against Supermemory."""
        query = request.data.get("query", "").strip()
        if not query:
            return _error("query is required")

        try:
            mem = _get_memory_service()
            results = mem.search_knowledge(
                query=query,
                filters=request.data.get("filters"),
                limit=request.data.get("limit", 10),
            )
            return _ok(results)
        except Exception as exc:
            logger.error(
                "Search failed: %s",
                exc,
                exc_info=True,
            )
            return _error(
                "Search service unavailable", 503
            )


# ------------------------------------------------------------------
# Gaps
# ------------------------------------------------------------------


@method_decorator(csrf_exempt, name="dispatch")
class KnowledgeGapListView(APIView):
    """GET: list all knowledge gaps."""

    def get(self, request: Request) -> Response:
        """Return all gaps ordered by newest first."""
        gaps = KnowledgeGap.objects.select_related(
            "assigned_employee",
        ).order_by("-created_at")
        serializer = KnowledgeGapSerializer(
            gaps, many=True
        )
        return _ok(serializer.data)


@method_decorator(csrf_exempt, name="dispatch")
class ResolveGapView(APIView):
    """POST {answer}: resolve a knowledge gap."""

    def post(self, request: Request, pk) -> Response:
        """Mark gap as resolved, create a new fact."""
        try:
            gap = KnowledgeGap.objects.get(pk=pk)
        except KnowledgeGap.DoesNotExist:
            return _error("Gap not found", 404)

        answer = request.data.get("answer", "").strip()
        if not answer:
            return _error("answer is required")

        gap.answer = answer
        gap.status = "resolved"
        gap.save()

        fact = KnowledgeFact.objects.create(
            content=answer,
            summary=gap.title[:500],
            category="tribal",
            source_type="manual",
            confidence_score=0.8,
        )
        gap.related_facts.add(fact)

        return _ok(
            {
                "gap": KnowledgeGapSerializer(gap).data,
                "created_fact": KnowledgeFactSerializer(
                    fact
                ).data,
            }
        )


# ------------------------------------------------------------------
# Employees
# ------------------------------------------------------------------


@method_decorator(csrf_exempt, name="dispatch")
class EmployeeListCreateView(APIView):
    """GET / POST employees."""

    def get(self, request: Request) -> Response:
        """List all employees."""
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(
            employees, many=True
        )
        return _ok(serializer.data)

    def post(self, request: Request) -> Response:
        """Create a new employee."""
        serializer = EmployeeSerializer(
            data=request.data
        )
        if not serializer.is_valid():
            return _error(json.dumps(serializer.errors))
        serializer.save()
        return _ok(
            serializer.data,
            http_status.HTTP_201_CREATED,
        )


@method_decorator(csrf_exempt, name="dispatch")
class EmployeeDetailView(APIView):
    """GET / PUT a single employee."""

    def get(self, request: Request, pk) -> Response:
        """Return a single employee."""
        try:
            emp = Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return _error("Employee not found", 404)
        return _ok(EmployeeSerializer(emp).data)

    def put(self, request: Request, pk) -> Response:
        """Update an employee."""
        try:
            emp = Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return _error("Employee not found", 404)
        serializer = EmployeeSerializer(
            emp, data=request.data, partial=True
        )
        if not serializer.is_valid():
            return _error(json.dumps(serializer.errors))
        serializer.save()
        return _ok(serializer.data)


@method_decorator(csrf_exempt, name="dispatch")
class EmployeeProfileView(APIView):
    """GET: Supermemory knowledge profile for an employee."""

    def get(self, request: Request, pk) -> Response:
        """Fetch aggregated knowledge profile from Supermemory.

        Returns:
            employee: Employee details from Django DB.
            profile.static: Long-term facts about this employee.
            profile.dynamic: Recent context and activity.
            related_facts: Facts linked to this employee's container.
        """
        try:
            emp = Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return _error("Employee not found", 404)

        try:
            mem = _get_memory_service()
            profile = mem.get_employee_profile(
                employee_id=str(emp.id),
                query=request.query_params.get("q", ""),
            )
            return _ok(
                {
                    "employee": EmployeeSerializer(emp).data,
                    "supermemory_profile": profile,
                }
            )
        except Exception as exc:
            logger.error(
                "Profile fetch failed for %s: %s",
                pk,
                exc,
                exc_info=True,
            )
            # Return employee data even if Supermemory is down
            return _ok(
                {
                    "employee": EmployeeSerializer(emp).data,
                    "supermemory_profile": {
                        "employee_id": str(emp.id),
                        "static": "",
                        "dynamic": "",
                        "related_facts": [],
                    },
                    "warning": "Supermemory profile unavailable",
                }
            )


# ------------------------------------------------------------------
# Interview
# ------------------------------------------------------------------


@method_decorator(csrf_exempt, name="dispatch")
class InterviewView(APIView):
    """POST {message}: chat with the agent in interview mode."""

    def post(self, request: Request, pk) -> Response:
        """Send a message in interview context."""
        try:
            emp = Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return _error("Employee not found", 404)

        message = request.data.get("message", "").strip()
        if not message:
            return _error("message is required")

        try:
            agent = _get_knowledge_agent()
            questions = agent.generate_interview_questions(
                employee_name=emp.name,
                role=emp.role or "",
                department=emp.department or "",
                expertise=emp.expertise_areas or [],
            )
            # Also chat-style follow-up if message provided
            answer = agent.chat(query=message).get("answer", "")
            return _ok(
                {"questions": questions, "agent_response": answer}
            )
        except Exception as exc:
            logger.error(
                "Interview failed for %s: %s",
                pk,
                exc,
                exc_info=True,
            )
            return _error(
                "Agent service unavailable", 503
            )


# ------------------------------------------------------------------
# Agent endpoints
# ------------------------------------------------------------------


@method_decorator(csrf_exempt, name="dispatch")
class AgentChatView(APIView):
    """POST {query}: ask the knowledge agent anything."""

    def post(self, request: Request) -> Response:
        """Return answer + sources from the agent.

        Also persists the Q&A exchange to Supermemory so that
        future queries can recall past conversations as context.
        """
        query = request.data.get("query", "").strip()
        if not query:
            return _error("query is required")

        try:
            agent = _get_knowledge_agent()
            result = agent.chat(query=query)
            answer = result.get("answer", "")

            # Persist Q&A exchange to Supermemory for future RAG context
            try:
                mem = _get_memory_service()
                conversation = f"user: {query}\nassistant: {answer}"
                mem.store_conversation(
                    employee_id="global_chat",
                    role="exchange",
                    content=conversation,
                )
            except Exception as sm_exc:
                # Non-fatal — answer already generated
                logger.warning(
                    "Conversation persistence failed (non-fatal): %s",
                    sm_exc,
                )

            return _ok(
                {
                    "answer": answer,
                    "sources": result.get("sources", []),
                }
            )
        except Exception as exc:
            logger.error(
                "Agent chat failed: %s",
                exc,
                exc_info=True,
            )
            return _error(
                "Agent service unavailable", 503
            )


@method_decorator(csrf_exempt, name="dispatch")
class ExtractFactsView(APIView):
    """POST {text}: extract facts using KnowledgeAgent."""

    def post(self, request: Request) -> Response:
        """Extract facts from free text, persist to DB + Supermemory.

        Previously facts were extracted and returned but never saved.
        Now each fact is:
          1. Saved to the Django KnowledgeFact table.
          2. Sent to Supermemory with a stable custom_id for dedup.
        """
        text = request.data.get("text", "").strip()
        if not text:
            return _error("text is required")

        try:
            agent = _get_knowledge_agent()
            raw_facts = agent.extract_facts(text=text)
        except Exception as exc:
            logger.error(
                "Fact extraction failed: %s",
                exc,
                exc_info=True,
            )
            return _error("Agent service unavailable", 503)

        saved_facts = []
        mem = _get_memory_service()

        for f in raw_facts:
            # 1. Persist to Django DB
            try:
                fact = KnowledgeFact.objects.create(
                    content=f.get("content", ""),
                    summary=f.get("summary", "")[:500],
                    category=f.get("category", "tribal"),
                    status=f.get("status", "current"),
                    confidence_score=float(
                        f.get("confidence_score", 0.5)
                    ),
                    source_type="document",
                    tags=f.get("tags", []),
                )
            except Exception as db_exc:
                logger.error(
                    "Failed to save extracted fact to DB: %s",
                    db_exc,
                )
                continue

            # 2. Send to Supermemory with stable custom_id
            try:
                mem.store_fact(
                    {
                        "content": fact.content,
                        "category": fact.category,
                        "confidence_score": fact.confidence_score,
                        "source": "document",
                        "tags": fact.tags,
                        "custom_id": f"fact_{fact.id}",
                    }
                )
            except Exception as sm_exc:
                logger.error(
                    "Supermemory store failed for fact %s: %s",
                    fact.id,
                    sm_exc,
                )
                # Non-fatal — fact already in DB

            saved_facts.append(
                KnowledgeFactSerializer(fact).data
            )

        return _ok(
            {"extracted": len(saved_facts), "facts": saved_facts}
        )


@method_decorator(csrf_exempt, name="dispatch")
class DetectGapsView(APIView):
    """POST: run gap detection on existing facts."""

    def post(self, request: Request) -> Response:
        """Detect gaps in current knowledge base."""
        try:
            agent = _get_knowledge_agent()
            facts = list(
                KnowledgeFact.objects.values(
                    "content", "category", "status"
                )[:50]
            )
            gaps_data = agent.detect_knowledge_gaps(facts=facts)
            # Persist detected gaps to DB
            created = 0
            for g in gaps_data:
                KnowledgeGap.objects.get_or_create(
                    title=g.get("title", "")[:255],
                    defaults={
                        "description": g.get("description", ""),
                        "severity": g.get("severity", "medium"),
                        "suggested_question": g.get(
                            "suggested_question", ""
                        ),
                    },
                )
                created += 1
            return _ok(
                {"gaps": gaps_data, "gaps_created": created}
            )
        except Exception as exc:
            logger.error(
                "Gap detection failed: %s",
                exc,
                exc_info=True,
            )
            return _error(
                "Agent service unavailable", 503
            )


@method_decorator(csrf_exempt, name="dispatch")
class GenerateOnboardingView(APIView):
    """POST {employee_id, role}: generate onboarding plan."""

    def post(self, request: Request) -> Response:
        """Generate a personalised onboarding plan."""
        employee_id = request.data.get("employee_id")
        role = request.data.get("role", "").strip()

        if not employee_id:
            return _error("employee_id is required")

        try:
            emp = Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            return _error("Employee not found", 404)

        try:
            agent = _get_knowledge_agent()
            facts = list(
                KnowledgeFact.objects.values(
                    "content", "summary", "category"
                )[:25]
            )
            plan_data = agent.build_onboarding_plan(
                role=role or emp.role or "",
                department=emp.department or "",
                facts=facts,
            )

            plan = OnboardingPlan.objects.create(
                employee=emp,
                title=plan_data.get(
                    "title",
                    f"Onboarding: {emp.name}",
                ),
                role_focus=role or emp.role or "",
                plan_data=plan_data,
            )

            return _ok(
                OnboardingPlanSerializer(plan).data,
                http_status.HTTP_201_CREATED,
            )
        except Employee.DoesNotExist:
            return _error("Employee not found", 404)
        except Exception as exc:
            logger.error(
                "Onboarding generation failed: %s",
                exc,
                exc_info=True,
            )
            return _error(
                "Agent service unavailable", 503
            )
