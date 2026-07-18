# 🔮 AGENT.md — LegacyLens Development Rules & Standards

> **This file is the single source of truth for all coding agents and developers.**
> Every code change MUST comply with these rules. No exceptions.

---

## 1. PROJECT IDENTITY

```
Project Name  : LegacyLens
Tagline       : Local Organisational Memory Agent
Type          : Django 5.x Web Application + REST API
Python        : 3.10+ (developed on 3.13.2)
Database      : SQLite (development), PostgreSQL (production)
Memory Layer  : Supermemory Local (localhost:6767)
LLM Provider  : NVIDIA NIM (OpenAI-compatible, free tier)
Hackathon     : Supermemory Local Hackathon (localhost:6767)
License       : MIT
```

### Branding Rules
- **NEVER** use "legacylens" anywhere in code, comments, docs, UI, or logs
- **ALWAYS** use "LegacyLens" as the project name
- The Python package name is `legacylens` (all lowercase, no hyphens)
- The Django settings module is `legacylens.settings.development`
- Import prefix: `from legacylens.` not `from legacylens.`

---

## 2. ARCHITECTURE RULES

### Layer Architecture (Top → Bottom)
```
┌─────────────────────────────────────┐
│  Templates (HTML/CSS/JS)            │  ← Presentation
├─────────────────────────────────────┤
│  Django Views / REST API Views      │  ← Controllers
├─────────────────────────────────────┤
│  Services (business logic)          │  ← Business Logic
├─────────────────────────────────────┤
│  Models (Django ORM)                │  ← Data Access
├─────────────────────────────────────┤
│  Core (memory, agent, formatters)   │  ← Infrastructure
├─────────────────────────────────────┤
│  Supermemory Local (localhost:6767)  │  ← External Memory
│  NVIDIA NIM API                     │  ← External LLM
└─────────────────────────────────────┘
```

### Strict Dependency Rules
- **Views** may import from **Services** and **Models** only
- **Services** may import from **Models** and **Core** only
- **Models** must NEVER import from Views or Services
- **Core** modules are infrastructure — they must NOT import from `apps/`
- **Templates** access data through context variables only, never import Python
- **NEVER** create circular imports. If you detect one, refactor immediately.

### App Boundaries
```
legacylens/
├── apps/
│   ├── core/          # Base models, health check, index view, web UI serving
│   ├── api/           # Lightweight status endpoints
│   ├── documents/     # Document upload, parsing, chunking
│   └── knowledge/     # Knowledge graph, facts, gaps, employees, onboarding
├── core/
│   ├── memory/        # Supermemory Local client + service
│   ├── agent/         # Knowledge agent (LLM calls, fact extraction, gap detection)
│   ├── conversation/  # Conversation interface (abstract + implementations)
│   ├── rag/           # RAG templates and context service
│   └── formatters/    # Response formatting (markdown, etc.)
```

### What Was REMOVED (Do NOT Re-Add)
- ❌ `apps/bot/` — Slack bot integration (entire directory deleted)
- ❌ `apps/search/` — Azure Cognitive Search (replaced by Supermemory)
- ❌ `apps/users/` — Standalone user app (merged into knowledge/Employee model)
- ❌ `core/kernel/` — Semantic Kernel factory (replaced by direct OpenAI calls)
- ❌ `core/azure_utils/` — Azure client manager (not needed locally)
- ❌ `skills/` — Semantic Kernel skills (replaced by agent system)
- ❌ All Azure SDK dependencies
- ❌ All Slack SDK dependencies
- ❌ All Bot Framework dependencies
- ❌ `semantic-kernel` dependency
- ❌ `psycopg2-binary` (not needed for SQLite dev)

---

## 3. CODING STANDARDS

### Python Style
```python
# Line length: 88 characters (Black/Ruff default)
# Quote style: double quotes
# Indent: 4 spaces
# Trailing commas: always in multi-line structures
# Type hints: encouraged but not mandatory (Python 3.10+ syntax)
# Docstrings: Google style
```

### Naming Conventions
```python
# Files:          snake_case.py
# Classes:        PascalCase
# Functions:      snake_case
# Variables:      snake_case
# Constants:      UPPER_SNAKE_CASE
# Django Models:  PascalCase (singular noun: KnowledgeFact, not KnowledgeFacts)
# Django Apps:    snake_case (knowledge, documents, core)
# URLs:           kebab-case (/api/knowledge/gaps/)
# Template files: snake_case.html
# CSS classes:    kebab-case (.knowledge-node, .fact-card)
# JS functions:   camelCase
# JSON keys:      snake_case
```

### Import Order (enforced by Ruff isort)
```python
# 1. Standard library
import os
import uuid
from typing import Any

# 2. Third-party
from django.db import models
from rest_framework import views
from openai import OpenAI

# 3. Local application (always use full path from legacylens)
from legacylens.apps.core.models import TimeStampedModel
from legacylens.core.memory.client import get_supermemory_client
```

### Django Model Rules
- Every model MUST inherit from `TimeStampedModel` (provides `created_at`, `modified_at`)
- Use `UUIDField` as primary key for all new models: `id = models.UUIDField(primary_key=True, default=uuid.uuid4)`
- Always define `__str__()` method
- Always define `class Meta` with at least `ordering`
- Use `JSONField` for flexible metadata, not separate tables for key-value pairs
- Foreign keys MUST specify `on_delete` explicitly
- Related names MUST be descriptive: `related_name="contributed_facts"` not `related_name="facts"`

### View Rules
- Use Django REST Framework `APIView` for all REST endpoints
- Use standard Django views for template rendering
- Every view MUST have a docstring explaining what it does
- Every endpoint MUST return JSON with consistent structure:
  ```python
  # Success
  {"status": "ok", "data": {...}}
  
  # Error
  {"status": "error", "message": "Human readable error", "code": "ERROR_CODE"}
  ```
- ALWAYS use `@csrf_exempt` for API endpoints that receive POST
- NEVER catch bare `Exception` without logging it

### Error Handling
```python
# CORRECT — specific exception, logged, graceful degradation
try:
    result = memory_service.search_knowledge(query)
except ConnectionError:
    logger.error("Supermemory Local unreachable at localhost:6767")
    return JsonResponse({"status": "error", "message": "Memory service unavailable"}, status=503)

# WRONG — silent failure, bare except
try:
    result = memory_service.search_knowledge(query)
except:
    pass
```

---

## 4. SUPERMEMORY LOCAL INTEGRATION RULES

### Connection
```python
# ALWAYS use the singleton client
from legacylens.core.memory.client import get_supermemory_client

# NEVER instantiate Supermemory() directly in views or services
# NEVER hardcode the URL — use environment variables
```

### Container Tag Convention
```python
# Employee-scoped:    f"employee_{employee_id}"
# Project-scoped:     f"project_{project_name}"
# Organization-wide:  f"org_{org_name}"
# Category-scoped:    f"category_{category}"
# Status-scoped:      f"status_{status}"
# Conversation:       f"conversation_{session_id}"
```

### Metadata Convention
Every memory stored in Supermemory MUST include:
```python
metadata = {
    "fact_id": str(uuid),           # Link back to Django model
    "category": "architecture",      # From KnowledgeFact.category choices
    "status": "current",             # current/historical/deprecated/etc.
    "confidence": 0.8,               # 0.0–1.0
    "source_type": "document",       # interview/document/code/inferred/manual
    "source_employee": str(uuid),    # Who provided this knowledge
    "ingested_at": "2025-07-17",     # ISO date string
}
```

### Search Rules
- ALWAYS use `search_mode="hybrid"` (combines keyword + semantic)
- Default `threshold=0.5` for broad searches, `0.7` for precise matches
- Default `limit=10` unless specifically needed otherwise
- ALWAYS pass `container_tags` to scope searches appropriately

---

## 5. LLM / NVIDIA NIM RULES

### Configuration
```python
# Use OpenAI SDK with NVIDIA NIM base URL
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],        # nvapi-xxxxx
    base_url=os.environ["OPENAI_BASE_URL"],       # https://integrate.api.nvidia.com/v1
)
```

### Prompt Engineering Rules
- System prompts MUST be defined in `legacylens/core/agent/prompts.py` — NEVER inline
- Every LLM call MUST specify `temperature` explicitly
- For fact extraction: `temperature=0.1` (deterministic)
- For creative answers: `temperature=0.7`
- For interview questions: `temperature=0.5`
- ALWAYS include JSON schema in prompts when expecting structured output
- NEVER send raw user input to LLM without wrapping in a prompt template
- ALWAYS log LLM calls with query + response length (not full response — privacy)

### Cost Control
- NVIDIA NIM free tier has rate limits (~40 req/min)
- Cache Supermemory search results for identical queries within 60 seconds
- Batch fact extraction: process documents in chunks, not one API call per sentence
- Use `gpt-4o-mini` equivalent models for routine tasks, larger models for analysis

---

## 6. FRONTEND RULES

### Technology Stack
```
HTML:     Django templates (Jinja2-like)
CSS:      Vanilla CSS with CSS custom properties (variables)
JS:       Vanilla JavaScript (ES6+), NO frameworks (no React, no Vue)
Graphs:   D3.js v7 (loaded via CDN)
Icons:    Lucide Icons (loaded via CDN)
Fonts:    Inter (loaded via Google Fonts)
```

### Design System
```css
/* MANDATORY color palette — dark mode only */
--bg-primary:    #0a0e17;
--bg-secondary:  #111827;
--bg-card:       #1a1f2e;
--bg-input:      #0f1520;
--text-primary:  #e2e8f0;
--text-secondary:#94a3b8;
--text-muted:    #64748b;
--accent-blue:   #3b82f6;
--accent-purple: #8b5cf6;
--accent-green:  #10b981;
--accent-amber:  #f59e0b;
--accent-red:    #ef4444;
--border:        #1e293b;
--border-hover:  #334155;
```

### CSS Rules
- NO Tailwind CSS — only vanilla CSS
- ALL colors MUST use CSS custom properties (variables) — NEVER hardcode hex values
- Border radius: `8px` for cards, `6px` for inputs, `4px` for small elements
- Spacing: use multiples of 4px (4, 8, 12, 16, 24, 32, 48, 64)
- Font sizes: use `rem` units, never `px` for text
- Transitions: `all 0.2s ease` for hover effects, `0.3s` for state changes
- NEVER use `!important`
- ALWAYS use `box-sizing: border-box` (set globally)

### JavaScript Rules
- NO npm, NO bundlers — all JS is served from `static/js/`
- Use `fetch()` for API calls, NEVER XMLHttpRequest
- Use `async/await`, NEVER raw Promises with `.then()`
- Use `const` by default, `let` only when reassignment is needed, NEVER `var`
- DOM manipulation: use `querySelector` / `querySelectorAll`
- ALWAYS handle fetch errors with try/catch
- NEVER use `innerHTML` with user-supplied content (XSS risk)
- Use `textContent` or DOM element creation instead

### Template Rules
- Base template: `templates/base.html` (all pages extend this)
- Every page MUST have a `<title>` block
- Every interactive element MUST have a unique `id` attribute
- Forms MUST include `{% csrf_token %}`
- Static files: `{% load static %}` then `{% static 'path' %}`

---

## 7. TESTING RULES

### Test Structure
```
tests/
├── test_models.py          # Model validation, relationships
├── test_views.py           # API endpoint tests
├── test_memory_service.py  # Supermemory integration (mock client)
├── test_agent.py           # Knowledge agent (mock LLM calls)
└── test_documents.py       # Document upload and parsing
```

### Rules
- Use `pytest` + `pytest-django`
- ALWAYS mock external services (Supermemory, NVIDIA NIM)
- Use `factory_boy` for model factories
- Test file naming: `test_<module>.py`
- Test function naming: `test_<what>_<condition>_<expected>()`
  ```python
  def test_extract_facts_from_document_returns_list_of_facts():
  ```
- Minimum: every model, every API endpoint, every agent function must have at least one test
- Run with: `python manage.py test` or `pytest`

---

## 8. GIT RULES

### Commit Messages
```
Format: <type>: <description>

Types:
  feat:     New feature
  fix:      Bug fix
  refactor: Code restructuring (no behavior change)
  docs:     Documentation changes
  style:    Formatting, CSS changes
  test:     Adding/updating tests
  chore:    Dependencies, config, tooling

Examples:
  feat: add knowledge gap detection endpoint
  fix: handle empty document upload gracefully
  refactor: extract Supermemory client to singleton
  docs: update README with setup instructions
```

### Branch Naming
```
feature/<short-description>    # New features
fix/<short-description>        # Bug fixes
```

### Rules
- NEVER commit `.env` files (add to `.gitignore`)
- NEVER commit `db.sqlite3`
- NEVER commit `__pycache__/` or `.pyc` files
- NEVER commit `logs/` directory contents
- NEVER commit `media/` uploaded files
- ALWAYS commit `requirements/` files
- ALWAYS commit migration files

---

## 9. ENVIRONMENT & CONFIGURATION

### Required Environment Variables
```env
# MANDATORY
DJANGO_SETTINGS_MODULE=legacylens.settings.development
SUPERMEMORY_API_KEY=sm_xxxxx
SUPERMEMORY_BASE_URL=http://localhost:6767
OPENAI_API_KEY=nvapi-xxxxx
OPENAI_BASE_URL=https://integrate.api.nvidia.com/v1
OPENAI_MODEL=meta/llama-3.1-70b-instruct

# OPTIONAL
DJANGO_SECRET_KEY=your-secret-key
LEGACYLENS_ORG_NAME=Your Organization
```

### Settings Hierarchy
```
.env                          → Loaded by python-dotenv
settings/__init__.py          → Loads .env, then settings_loader, then env-specific
settings/settings_loader.py   → Applies defaults for missing env vars
settings/base.py              → Common settings (INSTALLED_APPS, MIDDLEWARE, etc.)
settings/development.py       → SQLite, DEBUG=True, dev logging
```

### NEVER Change
- `manage.py` entry point structure
- `TimeStampedModel` base class
- `settings/__init__.py` loading order
- Health check endpoint at `/healthz/`

---

## 10. SECURITY RULES

- NEVER log full API keys — log only last 4 characters
- NEVER store credentials in source code
- NEVER disable CSRF protection on template-rendered forms
- API endpoints receiving external POST data MUST use `@csrf_exempt` + token auth
- User-uploaded files MUST be validated (extension, size, content type)
- NEVER use `eval()` or `exec()` on user input
- NEVER pass user input directly to OS commands
- SQL queries MUST use Django ORM or parameterized queries — NEVER string interpolation

---

## 11. PERFORMANCE RULES

- Database queries: NEVER make queries inside loops (use `select_related` / `prefetch_related`)
- Supermemory searches: cache identical queries for 60 seconds
- LLM calls: batch where possible, never call per-word or per-sentence
- D3.js graph: limit to 500 nodes rendered at once (paginate if more)
- Document parsing: stream large files, don't load entire PDF into memory
- Static files: use Django's `{% static %}` tag, enable `ManifestStaticFilesStorage` in production

---

## 12. FILE SIZE LIMITS

- No single Python file should exceed 500 lines. If it does, split into modules.
- No single function should exceed 50 lines. Extract helpers.
- No single template should exceed 300 lines. Use `{% include %}` for components.
- CSS file: max 800 lines. Split by component if larger.
- JS file: max 400 lines. Split by feature (graph.js, chat.js, etc.)

---

*Last updated: 2026-07-17*
*Maintained by: LegacyLens Development Team*
