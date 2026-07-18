"""KnowledgeAgent — the brain of LegacyLens.

Uses OpenAI-compatible API (NVIDIA NIM) for:
- Fact extraction from documents
- Contradiction analysis between old and new facts
- Knowledge gap detection
- Exit interview question generation
- Onboarding plan creation
- RAG-powered Q&A
"""

import json
import logging
import os
from typing import Any

from openai import OpenAI

from legacylens.core.agent.prompts import (
    CHAT_SYSTEM_PROMPT,
    CONTRADICTION_ANALYSIS_PROMPT,
    FACT_EXTRACTION_PROMPT,
    GAP_DETECTION_PROMPT,
    INTERVIEW_QUESTION_PROMPT,
    ONBOARDING_PLAN_PROMPT,
)
from legacylens.core.memory.service import MemoryService

logger = logging.getLogger(__name__)


class KnowledgeAgent:
    """Orchestrates all LLM-powered knowledge operations.

    Attributes:
        client: OpenAI-compatible client (NVIDIA NIM or OpenAI).
        model: The model identifier to use for completions.
        memory: The MemoryService for Supermemory integration.
    """

    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get(
                "OPENAI_BASE_URL",
                "https://integrate.api.nvidia.com/v1",
            ),
        )
        self.model = os.environ.get(
            "OPENAI_MODEL", "meta/llama-3.1-70b-instruct"
        )
        self.memory = MemoryService()

    def _call_llm(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """Make a single LLM completion call.

        Args:
            prompt: The user prompt to send.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in response.

        Returns:
            The assistant's response text.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.error("LLM call failed: %s", exc, exc_info=True)
            return ""

    def _parse_json(self, text: str) -> Any:
        """Extract JSON from LLM response, handling markdown fences.

        Args:
            text: Raw LLM response that may contain JSON.

        Returns:
            Parsed JSON object, or empty list/dict on failure.
        """
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = lines[1:]  # Remove opening fence
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]  # Remove closing fence
            cleaned = "\n".join(lines)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning(
                "Failed to parse JSON from LLM response: %s",
                cleaned[:200],
            )
            return []

    # ------------------------------------------------------------------
    # Fact Extraction
    # ------------------------------------------------------------------

    def extract_facts(self, document_text: str) -> list[dict[str, Any]]:
        """Extract structured facts from a document.

        Args:
            document_text: The full text of the document.

        Returns:
            A list of fact dicts with content, summary, category,
            status, confidence_score, and tags.
        """
        prompt = FACT_EXTRACTION_PROMPT.format(
            document_text=document_text[:8000]
        )
        response = self._call_llm(prompt, temperature=0.1)
        facts = self._parse_json(response)

        if not isinstance(facts, list):
            logger.warning("Expected list from fact extraction, got %s", type(facts))
            return []

        logger.info("Extracted %d facts from document", len(facts))
        return facts

    # ------------------------------------------------------------------
    # Contradiction Analysis
    # ------------------------------------------------------------------

    def analyze_contradictions(
        self,
        new_fact: str,
        existing_facts: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Check if a new fact contradicts existing knowledge.

        Args:
            new_fact: The content of the new fact.
            existing_facts: List of existing fact dicts with
                at least a 'content' key.

        Returns:
            Dict with 'contradictions' list. Each contradiction
            has new_fact, existing_fact, type, resolution, explanation.
        """
        if not existing_facts:
            return {"contradictions": []}

        existing_text = "\n".join(
            f"- {f.get('content', '')}" for f in existing_facts[:15]
        )
        prompt = CONTRADICTION_ANALYSIS_PROMPT.format(
            new_fact=new_fact,
            existing_facts=existing_text,
        )
        response = self._call_llm(prompt, temperature=0.1)
        result = self._parse_json(response)

        if isinstance(result, dict):
            return result
        return {"contradictions": []}

    # ------------------------------------------------------------------
    # Knowledge Gap Detection
    # ------------------------------------------------------------------

    def detect_knowledge_gaps(
        self,
        facts: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Identify gaps in organizational knowledge.

        Args:
            facts: List of known fact dicts.

        Returns:
            List of gap dicts with title, description, severity,
            suggested_question, and related_topics.
        """
        if not facts:
            return []

        facts_text = "\n".join(
            f"- [{f.get('category', 'general')}] {f.get('content', '')}"
            for f in facts[:30]
        )
        prompt = GAP_DETECTION_PROMPT.format(facts=facts_text)
        response = self._call_llm(prompt, temperature=0.3)
        result = self._parse_json(response)

        if isinstance(result, dict) and "gaps" in result:
            logger.info("Detected %d knowledge gaps", len(result["gaps"]))
            return result["gaps"]
        return []

    # ------------------------------------------------------------------
    # Interview Questions
    # ------------------------------------------------------------------

    def generate_interview_questions(
        self,
        employee_name: str,
        role: str = "",
        department: str = "",
        expertise: list[str] | None = None,
    ) -> list[str]:
        """Generate exit interview questions for a departing employee.

        Args:
            employee_name: The employee's name.
            role: Their job title/role.
            department: Their department.
            expertise: List of expertise area strings.

        Returns:
            List of interview question strings.
        """
        prompt = INTERVIEW_QUESTION_PROMPT.format(
            employee_name=employee_name,
            role=role or "Unknown",
            department=department or "Unknown",
            expertise=", ".join(expertise or ["general"]),
        )
        response = self._call_llm(prompt, temperature=0.5)
        result = self._parse_json(response)

        if isinstance(result, dict) and "questions" in result:
            return result["questions"]
        return []

    # ------------------------------------------------------------------
    # Onboarding Plans
    # ------------------------------------------------------------------

    def build_onboarding_plan(
        self,
        role: str,
        department: str = "",
        facts: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Generate a personalized onboarding plan.

        Args:
            role: The new employee's role/title.
            department: Their department.
            facts: Available knowledge facts to draw from.

        Returns:
            Dict with title, total_duration_days, and phases array.
        """
        knowledge_summary = "\n".join(
            f"- [{f.get('category', '')}] {f.get('summary', f.get('content', '')[:80])}"
            for f in (facts or [])[:25]
        )
        prompt = ONBOARDING_PLAN_PROMPT.format(
            role=role,
            department=department or "General",
            knowledge_summary=knowledge_summary or "No knowledge available yet.",
        )
        response = self._call_llm(prompt, temperature=0.5)
        result = self._parse_json(response)

        if isinstance(result, dict):
            return result
        return {"title": f"Onboarding Plan for {role}", "phases": []}

    # ------------------------------------------------------------------
    # Chat (RAG-Powered Q&A)
    # ------------------------------------------------------------------

    def chat(
        self,
        query: str,
        context: str = "",
    ) -> dict[str, Any]:
        """Answer a question using organizational memory context.

        If no context is provided, automatically searches Supermemory
        for relevant facts.

        Args:
            query: The user's question.
            context: Pre-built context string. If empty, will
                search Supermemory automatically.

        Returns:
            Dict with 'answer' and 'sources' keys.
        """
        sources = []
        if not context:
            search_results = self.memory.search_knowledge(
                query=query, limit=5
            )
            context_parts = []
            for result in search_results:
                content = result.get("content", "")
                context_parts.append(content)
                sources.append(
                    {
                        "content": content[:200],
                        "score": result.get("score", 0.0),
                    }
                )
            context = "\n\n".join(context_parts) if context_parts else "No relevant context found."

        system_prompt = CHAT_SYSTEM_PROMPT.format(context=context)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ],
                temperature=0.7,
                max_tokens=2048,
            )
            answer = response.choices[0].message.content or ""
        except Exception as exc:
            logger.error("Chat LLM call failed: %s", exc, exc_info=True)
            answer = "I'm unable to answer right now. Please check that the LLM service is configured correctly."

        return {"answer": answer, "sources": sources}
