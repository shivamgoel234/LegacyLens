"""Seed demo employees for LegacyLens."""
import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "legacylens.settings.development"
)
django.setup()

from legacylens.apps.knowledge.models import Employee

employees = [
    {
        "name": "Priya Sharma",
        "email": "priya@company.com",
        "role": "Senior Database Administrator",
        "department": "Infrastructure",
        "expertise_areas": [
            "MySQL", "PostgreSQL", "backups",
            "replication", "database migration",
        ],
        "status": "departing",
    },
    {
        "name": "Rahul Verma",
        "email": "rahul@company.com",
        "role": "Lead Backend Engineer",
        "department": "Engineering",
        "expertise_areas": [
            "Java", "Spring Boot", "microservices",
            "payment systems", "Kubernetes",
        ],
        "status": "active",
    },
    {
        "name": "Anita Desai",
        "email": "anita@company.com",
        "role": "Junior DevOps Engineer",
        "department": "Infrastructure",
        "expertise_areas": [
            "GitHub Actions", "ArgoCD", "Docker",
        ],
        "status": "onboarding",
    },
]

for emp_data in employees:
    emp, created = Employee.objects.get_or_create(
        email=emp_data["email"],
        defaults=emp_data,
    )
    status = "CREATED" if created else "EXISTS"
    print(f"  {status}: {emp.name} ({emp.status})")

print(f"\nTotal employees: {Employee.objects.count()}")
