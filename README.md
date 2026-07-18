<div align="center">

# 🔍 LegacyLens

### **AI-Powered Organizational Memory for Engineering Teams**

*Stop losing institutional knowledge when employees leave.*
*LegacyLens captures, connects, and preserves the knowledge that lives in people's heads.*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![OpenAI](https://img.shields.io/badge/LLM-OpenAI_Compatible-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![Supermemory](https://img.shields.io/badge/Memory-Supermemory-FF6B6B?style=for-the-badge)](https://supermemory.ai)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

<img src="https://img.shields.io/badge/🏆_LocalHack_Hackathon-2026-gold?style=for-the-badge" alt="Hackathon Badge"/>

---

**[Features](#-features) · [Demo](#-quick-demo) · [Architecture](#-architecture) · [Setup](#-setup) · [API Reference](#-api-reference)**

</div>

<br/>

## 🎯 The Problem

> **67% of organizational knowledge walks out the door** when an employee leaves.
> — *Harvard Business Review*

Engineering teams lose critical context every time someone departs:
- 🧠 **Tribal knowledge** — *"Why did we choose PostgreSQL over MySQL?"*
- 🔧 **Undocumented processes** — *"How do we actually rollback a deployment?"*
- 🤝 **Ownership maps** — *"Who knows how the payment service really works?"*
- ⚡ **Decision history** — *"What did we try before this approach?"*

**LegacyLens** solves this by building a living **knowledge graph** from your documentation, extracting facts using AI, detecting gaps, and generating targeted exit interview questions — all before it's too late.

<br/>

## ✨ Features

### 📊 Interactive Knowledge Graph
Visualize your entire organization's technical knowledge as an interactive D3.js force-directed graph. See how architecture decisions connect, which facts supersede others, and where contradictions exist.

### 🤖 AI-Powered Q&A (RAG)
Ask natural language questions and get answers grounded in your actual documentation. Powered by **Retrieval-Augmented Generation** using Supermemory for semantic search and any OpenAI-compatible LLM.

### 📄 Smart Document Ingestion
Upload architecture docs, runbooks, or decision records. LegacyLens automatically:
- Extracts structured facts with categories and confidence scores
- Detects contradictions between old and new information
- Identifies which facts supersede others

### ⚠️ Knowledge Gap Detection
AI analyzes your knowledge base and surfaces what's **missing** — rollback procedures without documentation, systems without backup owners, decisions without rationale.

### 🎤 Exit Interview Generator
When an employee is departing, LegacyLens generates **targeted interview questions** based on their expertise areas to capture undocumented tribal knowledge before they leave.

### 🎓 Onboarding Plan Generator
For new joiners, automatically creates personalized onboarding plans based on their role and available organizational knowledge.

### 👥 Employee Knowledge Tracking
Track which employees own which knowledge domains. See who's departing, who's onboarding, and where knowledge transfer gaps exist.

<br/>

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     LegacyLens Web UI                       │
│  Dashboard │ Knowledge Graph │ Chat │ Docs │ Employees │ Gaps│
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │     Django REST API     │
              │   (DRF + APIView)       │
              └────────┬───────┬────────┘
                       │       │
          ┌────────────┘       └────────────┐
          ▼                                 ▼
┌──────────────────┐              ┌──────────────────┐
│  KnowledgeAgent  │              │  MemoryService   │
│  (LLM Brain)     │              │  (RAG Layer)     │
│                  │              │                  │
│ • Fact Extraction│              │ • Semantic Search│
│ • Gap Detection  │              │ • Doc Storage    │
│ • Contradictions │              │ • Profiles       │
│ • Interview Q's  │              │ • Container Tags │
│ • Onboarding     │              │                  │
└────────┬─────────┘              └────────┬─────────┘
         │                                 │
         ▼                                 ▼
┌──────────────────┐              ┌──────────────────┐
│  OpenAI-Compat   │              │   Supermemory    │
│  LLM Provider    │              │   Local Server   │
│                  │              │                  │
│ • Vercel Gateway │              │ • Vector Embeddings│
│ • NVIDIA NIM     │              │ • Hybrid Search  │
│ • OpenAI Direct  │              │ • Local Storage  │
│ • Ollama         │              │ • Encrypted DB   │
└──────────────────┘              └──────────────────┘
```

<br/>

## 🚀 Setup

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** (for Supermemory)
- An **OpenAI-compatible API key** (Vercel AI Gateway / NVIDIA NIM / OpenAI / Ollama)

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/legacylens.git
cd legacylens

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements/base.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your LLM API key | `vck_xxx` or `sk-xxx` |
| `OPENAI_BASE_URL` | OpenAI-compatible endpoint | `https://ai-gateway.vercel.sh/v1` |
| `OPENAI_MODEL` | Model identifier | `openai/gpt-4o-mini` |
| `SUPERMEMORY_API_KEY` | Auto-generated on first run | `sm_xxx` |
| `SUPERMEMORY_BASE_URL` | Supermemory server URL | `http://localhost:6767` |

### 3. Start Supermemory (Memory Layer)

```bash
# In a separate terminal (WSL/Linux recommended)
npx supermemory local
# Copy the API key from output to your .env file
```

### 4. Initialize Database & Run

```bash
python manage.py migrate
python manage.py runserver
```

Open **http://localhost:8000** — LegacyLens is running! 🎉

### 5. Seed Demo Data (Optional)

```bash
# Upload sample documents
# Go to Documents page → Upload architecture_v1.md and architecture_v2.md from demo_docs/

# Extract facts from documents
python extract_facts.py

# Generate relationships between facts
python gen_relationships.py

# Add demo employees
python seed_employees.py
```

<br/>

## 📡 API Reference

### Documents
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/documents/upload/` | Upload a document (PDF, DOCX, MD, TXT) |
| `GET` | `/api/documents/list/` | List all documents |
| `DELETE` | `/api/documents/<uuid>/delete/` | Delete a document |

### Knowledge Graph
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/knowledge/facts/` | List all facts |
| `POST` | `/api/knowledge/facts/` | Create a fact |
| `GET` | `/api/knowledge/graph/data/` | Graph nodes + edges (D3.js) |
| `POST` | `/api/knowledge/search/` | Semantic search |

### AI Agent
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/knowledge/agent/chat/` | Ask LegacyLens (RAG Q&A) |
| `POST` | `/api/knowledge/agent/extract/` | Extract facts from text |
| `POST` | `/api/knowledge/agent/gaps/detect/` | Detect knowledge gaps |
| `POST` | `/api/knowledge/agent/onboarding/` | Generate onboarding plan |

### Employees
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET/POST` | `/api/knowledge/employees/` | List / Create employees |
| `GET/PUT` | `/api/knowledge/employees/<uuid>/` | Get / Update employee |
| `POST` | `/api/knowledge/employees/<uuid>/interview/` | Exit interview questions |

### Knowledge Gaps
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/knowledge/gaps/` | List all gaps |
| `POST` | `/api/knowledge/gaps/<uuid>/resolve/` | Resolve a gap |

<br/>

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Django 6.0 + DRF | REST API, ORM, Admin |
| **Frontend** | Vanilla JS + D3.js | Interactive UI, Knowledge Graph |
| **LLM** | OpenAI-compatible API | Fact extraction, Q&A, Gap detection |
| **Memory** | Supermemory (Local) | Vector embeddings, Semantic search |
| **Database** | SQLite (dev) | Structured data storage |
| **Styling** | Custom CSS | Dark-mode premium UI |

<br/>

## 📁 Project Structure

```
legacylens/
├── core/
│   ├── agent/
│   │   ├── knowledge_agent.py   # LLM orchestrator (extract, chat, gaps)
│   │   └── prompts.py           # All LLM prompt templates
│   └── memory/
│       ├── client.py            # Supermemory SDK client
│       └── service.py           # High-level memory operations
├── apps/
│   ├── knowledge/               # Facts, Gaps, Employees, Relationships
│   ├── documents/               # Document upload & ingestion
│   └── core/                    # Web UI views
├── settings/                    # Django settings (dev/prod/test)
├── static/
│   ├── css/legacylens.css       # Complete design system
│   └── js/                      # Chat, Graph, Documents, Dashboard
└── templates/                   # Django HTML templates
    ├── dashboard.html
    ├── knowledge_graph.html
    ├── chat.html
    ├── documents.html
    ├── employees.html
    └── gaps.html
```

<br/>

## 🔌 Supported LLM Providers

LegacyLens works with **any OpenAI-compatible API**:

| Provider | Base URL | Free Tier |
|----------|----------|-----------|
| **Vercel AI Gateway** | `https://ai-gateway.vercel.sh/v1` | ✅ Yes |
| **NVIDIA NIM** | `https://integrate.api.nvidia.com/v1` | ✅ Yes |
| **OpenAI** | `https://api.openai.com/v1` | ❌ Paid |
| **Ollama** (local) | `http://localhost:11434/v1` | ✅ Free |
| **LM Studio** (local) | `http://localhost:1234/v1` | ✅ Free |

<br/>

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

<br/>

<div align="center">

---

**Built with ❤️ for the LocalHost Hackathon 2026**

*LegacyLens — Because organizational knowledge shouldn't walk out the door.*

</div>
