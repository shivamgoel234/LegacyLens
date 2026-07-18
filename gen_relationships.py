"""Generate relationships between extracted facts."""
import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "legacylens.settings.development"
)
django.setup()

from legacylens.apps.knowledge.models import (
    KnowledgeFact,
    KnowledgeRelationship,
)

facts = list(KnowledgeFact.objects.all())
print(f"Total facts: {len(facts)}")

# Find contradictions: v1 facts vs v2 facts by matching keywords
v1_facts = [f for f in facts if f.source_document and "v1" in f.source_document.title]
v2_facts = [f for f in facts if f.source_document and "v2" in f.source_document.title]

print(f"v1 facts: {len(v1_facts)}, v2 facts: {len(v2_facts)}")

keywords_map = {
    "database": ["mysql", "postgresql", "database", "db"],
    "deploy": ["jenkins", "github actions", "deployment", "deploy", "argocd"],
    "payment": ["payment", "monolith", "microservice"],
    "auth": ["jwt", "auth0", "authentication", "token", "sso"],
}

created = 0
for topic, keywords in keywords_map.items():
    topic_v1 = [f for f in v1_facts if any(k in f.content.lower() for k in keywords)]
    topic_v2 = [f for f in v2_facts if any(k in f.content.lower() for k in keywords)]

    for f1 in topic_v1:
        for f2 in topic_v2:
            # v2 supersedes v1
            rel, is_new = KnowledgeRelationship.objects.get_or_create(
                source=f2,
                target=f1,
                relationship_type="supersedes",
                defaults={"similarity_score": 0.85, "is_confirmed": True},
            )
            if is_new:
                created += 1
                print(f"  {topic}: '{f2.summary[:40]}' supersedes '{f1.summary[:40]}'")

        # Also create related links within same version
        for i, f_a in enumerate(topic_v1):
            for f_b in topic_v1[i+1:]:
                rel, is_new = KnowledgeRelationship.objects.get_or_create(
                    source=f_a,
                    target=f_b,
                    relationship_type="related",
                    defaults={"similarity_score": 0.6, "is_confirmed": True},
                )
                if is_new:
                    created += 1

        for i, f_a in enumerate(topic_v2):
            for f_b in topic_v2[i+1:]:
                rel, is_new = KnowledgeRelationship.objects.get_or_create(
                    source=f_a,
                    target=f_b,
                    relationship_type="related",
                    defaults={"similarity_score": 0.6, "is_confirmed": True},
                )
                if is_new:
                    created += 1

total_rels = KnowledgeRelationship.objects.count()
print(f"\nCreated {created} new relationships")
print(f"=== TOTAL RELATIONSHIPS: {total_rels} ===")
