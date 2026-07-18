"""Extract facts from all uploaded documents."""
import os
import sys
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "legacylens.settings.development"
)
django.setup()

from legacylens.core.agent.knowledge_agent import KnowledgeAgent
from legacylens.apps.documents.models import Document
from legacylens.apps.knowledge.models import KnowledgeFact

agent = KnowledgeAgent()

for doc in Document.objects.all():
    print(f"\n--- Extracting from: {doc.title} ---")
    try:
        with open(doc.file_path, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"Content: {len(content)} chars")

        facts = agent.extract_facts(content)
        print(f"LLM returned {len(facts)} facts")

        for fact_data in facts:
            summary = fact_data.get("summary", "")
            fact_content = fact_data.get("content", summary)
            category = fact_data.get("category", "architecture")
            valid_categories = [
                "architecture", "process", "tooling",
                "domain", "decision", "ownership",
                "onboarding", "tribal",
            ]
            if category not in valid_categories:
                category = "architecture"

            fact = KnowledgeFact.objects.create(
                content=fact_content,
                summary=summary[:500] if summary else fact_content[:500],
                category=category,
                status="current",
                confidence_score=fact_data.get("confidence", 0.8),
                source_document=doc,
                source_type="document",
            )
            print(f"  + [{category}] {fact.summary[:70]}")

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

total = KnowledgeFact.objects.count()
print(f"\n=== TOTAL FACTS IN DB: {total} ===")
