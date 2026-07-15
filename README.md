# ⚡ EnterpriseLead AI — B2B Lead Qualification Agent

> **FlowZint AI Hackathon 2026** — Gold Tier Submission  
> *From Website Visitor to Qualified Lead in Under 3 Minutes*

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)
[![Claude](https://img.shields.io/badge/Claude-3.5_Sonnet-orange?logo=anthropic)](https://anthropic.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-purple)](LICENSE)

---

## 🎯 What Is This?

**EnterpriseLead AI** is an autonomous B2B SaaS lead qualification agent. It replaces the typical "fill out a form" experience with a **natural, multi-turn AI conversation** powered by Claude 3.5 Sonnet — then scores the lead across **5 business dimensions** and routes hot leads directly to your CRM and sales team in real-time.

### The Problem
Sales teams waste 40% of their time chasing unqualified leads. Traditional lead forms produce low-quality data and cold emails feel impersonal.

### The Solution
A conversational AI agent that:
- **Engages** prospects naturally (2-min conversation)
- **Qualifies** them across 5 dimensions (ICP, Intent, Timeline, Authority, Engagement)
- **Scores** 0-100 using Claude's deep reasoning
- **Routes** hot leads (75+) instantly via HubSpot + SMS + email

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **Conversational AI** | Multi-turn Claude 3.5 Sonnet with BANT-Extended consultative system prompt |
| 🎯 **5-Dimension Scoring** | ICP (30%) + Intent (25%) + Timeline (20%) + Authority (15%) + Engagement (10%) |
| 📊 **Elite Score Card** | Animated score circle + strengths/gaps cards + strategic next-step recommendations |
| 🔗 **HubSpot CRM Sync** | Create-or-update contacts with lead score and stage |
| 🔔 **Instant Alerts** | Twilio SMS + SendGrid HTML email for hot leads (score ≥ 75) |
| 📈 **Analytics Dashboard** | Pipeline snapshot, 7-day metrics, hot leads list |
| 🗄️ **Full Persistence** | PostgreSQL with conversation history, lead records, score snapshots |
| 🚀 **Production Ready** | Railway + Vercel deployment, Docker Compose for local dev |

---

## ⚡ Elite AI Features

### Intelligent Chat System
- **BANT-Extended Sales Methodology** — Budget, Authority, Need, Timeline + Competition + Use Case
- **Stage-Aware Conversation Guidance** — 5 adaptive stages: Opening → Diagnosis → Discovery → Qualification → Closing
- **Consultative (Not Pushy) Approach** — Understands before selling, qualifies OUT as well as IN
- **Context-Aware Memory** — References details from earlier in the conversation
- **Elite Language Patterns** — "That's common in [industry]...", "Help me understand...", "What I'm hearing is..."

### Sophisticated Lead Scoring Engine
- **Detailed BANT Rubric** — 5 score bands (0–39 / 40–59 / 60–74 / 75–89 / 90–100) per dimension
- **Evidence-Based Analysis** — Claude cites specific quotes and signals from the conversation
- **Business-Driven Reasoning** — Connects scores to revenue impact and organizational dynamics
- **Three New Intelligence Fields:**
  - `key_strengths` — Top 1–2 positive factors making this lead compelling
  - `key_gaps` — Top 1–2 risks or limiting factors to be aware of
  - `next_step` — Specific action for the sales or marketing team
- **Routing Logic** — `≥75 → Sales` | `50–74 → Nurture` | `<50 → Marketing Only`

### Enhanced Score Card UI
- **Recommendation Pill** — Color-coded routing decision (🔴 Hot / 🟡 Warm / 🔵 Cold)
- **Key Strengths Card** — Green callout showing what makes this lead compelling
- **Areas to Develop Card** — Amber callout highlighting risks or gaps
- **Recommended Next Step** — Actionable team guidance matched to recommendation color
- **Hover Tooltips** — Dimension descriptions on hover for contextual understanding

---

## 🏗️ Architecture

```
React Frontend (Vercel)
    │
    ▼ REST API
FastAPI Backend (Railway)
    ├── Claude 3.5 Sonnet    → Qualification + Scoring
    ├── PostgreSQL           → Conversation + Lead persistence
    ├── HubSpot CRM          → Contact sync
    ├── Twilio               → SMS hot lead alerts
    └── SendGrid             → Email hot lead alerts
```

**Full architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (or use Docker Compose)
- Anthropic API key

### Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/Alquama-Shaibli/Sales-Bot-.git
cd Sales-Bot-

# 2. Backend
cd backend
cp .env.example .env
# Fill in ANTHROPIC_API_KEY + DATABASE_URL in .env

pip install -r requirements.txt
uvicorn main:app --reload
# → Backend at http://localhost:8000
# → Swagger UI at http://localhost:8000/docs

# 3. Frontend (new terminal)
cd frontend
npm install
REACT_APP_API_URL=http://localhost:8000 npm start
# → UI at http://localhost:3000
```

### Docker Compose (Full Stack)

```bash
# From repo root (sets up backend + postgres)
docker-compose up --build

# Backend: http://localhost:8000
# Docs:    http://localhost:8000/docs
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/conversation/start` | Start qualification session |
| `POST` | `/api/message` | Send user message, get AI reply |
| `POST` | `/api/score` | Score the full conversation |
| `POST` | `/api/lead/qualify` | Qualify lead + CRM sync + alert |
| `GET` | `/api/leads` | Get all leads (filterable) |
| `GET` | `/api/analytics/pipeline` | Pipeline health metrics |
| `GET` | `/api/analytics/hot-leads` | All hot leads (≥75) |
| `GET` | `/api/analytics/daily-metrics` | 7-day breakdown |
| `GET` | `/api/analytics/alerts-status` | Alert channel config status |

Full API reference: [docs/API.md](docs/API.md)

---

## 🔑 Environment Variables

Copy `backend/.env.example` → `backend/.env`:

```env
# Required
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Optional — CRM
HUBSPOT_API_KEY=pat-na1-xxxxx

# Optional — Alerts
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_FROM=+1XXXXXXXXXX
SALES_ALERT_PHONE=+91XXXXXXXXXX
SENDGRID_API_KEY=SG.xxxxx
SALES_EMAIL=sales@yourcompany.com
LEAD_SCORE_THRESHOLD=75
```

---

## 🧪 Tests

```bash
cd backend
pip install pytest pytest-asyncio
pytest tests/ -v

# Output:
# tests/test_chat.py::TestGetOpeningMessage::test_returns_string PASSED
# tests/test_scoring.py::TestScoreConversation::test_hot_lead_score_range PASSED
# tests/test_hubspot.py::TestSyncLead::test_sync_lead_returns_none_when_disabled PASSED
# ... (20+ tests)
```

---

## 📁 Project Structure

```
Sales-Bot-/
├── backend/
│   ├── main.py              ← FastAPI app factory
│   ├── config.py            ← Pydantic settings
│   ├── models.py            ← SQLAlchemy ORM
│   ├── schemas.py           ← Pydantic schemas
│   ├── routers/             ← API endpoints
│   ├── services/            ← Business logic
│   ├── migrations/          ← SQL migrations
│   ├── tests/               ← Unit tests
│   └── Dockerfile
├── frontend/
│   └── src/
│       ├── components/      ← ChatWidget, ScoreCard, Message...
│       └── hooks/           ← useChat, useScore, useApi
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEPLOYMENT.md
├── docker-compose.yml
├── vercel.json
└── brain.md                 ← Live build tracker
```

---

## 🏆 FlowZint Hackathon — Submission Checklist

- [x] Multi-turn conversational AI agent
- [x] Claude 3.5 Sonnet integration
- [x] 5-dimension weighted scoring engine
- [x] HubSpot CRM integration
- [x] Real-time SMS + email alerts for hot leads
- [x] Beautiful React frontend with glassmorphism UI
- [x] Full PostgreSQL persistence
- [x] Pipeline analytics dashboard
- [x] Unit tests (chat, scoring, HubSpot)
- [x] Railway + Vercel deployment ready
- [x] Docker Compose local setup
- [x] Full documentation (Architecture + API + Deployment)
- [x] 25+ git commits with clear history
- [x] **Elite BANT-Extended consultative system prompt**
- [x] **Stage-aware conversation detection (5 stages)**
- [x] **BANT scoring rubric with 5-band granularity**
- [x] **key_strengths / key_gaps / next_step scoring fields**
- [x] **Enhanced ScoreCard with strengths/gaps/recommendation UI**

---

## 📊 Build Progress

| Day | Focus | Status |
|-----|-------|--------|
| Day 1 | Project setup + Backend scaffolding | ✅ Complete |
| Day 2 | Claude integration + 5-dim scoring | ✅ Complete |
| Day 3 | PostgreSQL + CRUD + Repository pattern | ✅ Complete |
| Day 4 | React UI (ChatWidget + ScoreCard) | ✅ Complete |
| Day 5 | HubSpot + Alerts + Analytics API | ✅ Complete |
| Day 6 | Tests + Architecture + API docs | ✅ Complete |
| Day 7 | Deployment config + Final polish | ✅ Complete |
| **Elite Upgrade** | **BANT prompts + Stage detection + BANT scoring + ScoreCard** | **⚡ Complete** |

---

## 👨‍💻 Author

**Alquama Shaibli** — FlowZint Hackathon 2026  
📧 alquama.r56@gmail.com  
🔗 [GitHub](https://github.com/Alquama-Shaibli/Sales-Bot-)

---

*Built with ❤️ using Claude AI, FastAPI, and React — FlowZint 2026*
