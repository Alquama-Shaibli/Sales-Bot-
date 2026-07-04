# 🎯 EnterpriseLead AI — FlowZint Hackathon 2026

> **"From Website Visitor to Qualified Lead in 3 Minutes"**

[![Live Demo](https://img.shields.io/badge/Live-Demo-green)](https://your-railway-url)
[![GitHub](https://img.shields.io/badge/GitHub-Repo-blue)](https://github.com/Alquama-Shaibli/Sales-Bot-)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 🚀 What Is This?

**EnterpriseLead AI** is an autonomous AI agent that qualifies B2B SaaS leads through intelligent multi-turn conversation, scores them in real-time across 5 dimensions, and automatically syncs qualified leads to HubSpot CRM — no manual data entry required.

**Built for:** FlowZint AI Hackathon 2026 — Gold Tier submission

---

## 🔥 The Problem

| Metric | Value |
|--------|-------|
| Average B2B SaaS Cost Per Lead | **$237** |
| MQL → SQL conversion rate | **13%** (87% waste) |
| Time sales reps spend qualifying | **20 min/lead** |
| Time spent actually selling | **28% of their day** |

---

## ✅ The Solution

EnterpriseLead AI automates the entire lead qualification process:

1. **Prospect visits your site** → starts chatting with the bot
2. **Bot has a natural conversation** → asks the right questions in the right order
3. **Lead is scored 0–100** → across 5 weighted dimensions
4. **Auto-synced to HubSpot** → with score, notes, and custom fields
5. **Sales team gets an SMS alert** → for hot leads (score > 75)

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.11) |
| LLM | Claude 3.5 Sonnet (Anthropic) |
| Database | PostgreSQL (Railway) |
| Frontend | React + TailwindCSS |
| CRM | HubSpot API |
| Alerts | Twilio SMS + SendGrid Email |
| Deployment | Railway |

---

## 📊 Lead Scoring System

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| ICP Fit | **30%** | Company size, industry, growth stage |
| Intent Signals | **25%** | Urgency, pain severity, language |
| Timeline | **20%** | When they want to buy |
| Authority | **15%** | Decision-making power |
| Engagement | **10%** | Response quality |

- **75–100** 🔴 Hot Lead → Routed to Sales immediately
- **50–74** 🟡 Warm Lead → Nurture sequence
- **0–49** 🔵 Cold Lead → Marketing only

---

## ⚡ Quick Start (5 minutes)

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (or use Supabase free tier)

### Backend Setup
```bash
git clone https://github.com/Alquama-Shaibli/Sales-Bot-.git
cd Sales-Bot-/backend

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

cp .env.example .env
# Edit .env with your API keys

python main.py
# → API running at http://localhost:8000
```

### Frontend Setup
```bash
cd ../frontend
npm install
npm start
# → App running at http://localhost:3000
```

---

## 🔑 Required API Keys

| Service | Where to Get | Required? |
|---------|-------------|----------|
| Anthropic Claude | [console.anthropic.com](https://console.anthropic.com) | ✅ Yes |
| HubSpot | [hubspot.com](https://hubspot.com) → Private Apps | ✅ Yes |
| PostgreSQL | [railway.app](https://railway.app) or [supabase.com](https://supabase.com) | ✅ Yes |
| Twilio (SMS) | [twilio.com](https://twilio.com) | ⚪ Optional |
| SendGrid (Email) | [sendgrid.com](https://sendgrid.com) | ⚪ Optional |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/conversation/start` | Start a new chat session |
| POST | `/api/message` | Send a message, get AI response |
| POST | `/api/score` | Score the conversation (0–100) |
| POST | `/api/lead/qualify` | Sync lead to HubSpot |
| GET | `/api/conversations/{id}` | Get full conversation history |

---

## 🎯 Business Impact

- **40% cost reduction** per lead ($237 → ~$140)
- **3x lead qualification capacity** with same team
- **$400K+ annual revenue impact** for a $2M ARR company
- **171% average ROI** (BCG research on agentic AI)

---

## 📁 Project Structure

```
Sales-Bot-/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment settings
│   ├── database.py          # PostgreSQL connection
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic request/response models
│   ├── requirements.txt
│   ├── Dockerfile
│   └── routers/
│       ├── chat.py          # Chat endpoints
│       ├── leads.py         # Lead qualification endpoints
│       └── health.py        # Health check
│   └── services/
│       ├── chat_service.py      # Claude API integration
│       ├── scoring_service.py   # 5-dimension scoring engine
│       └── hubspot_service.py   # CRM sync
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── ChatWidget.jsx
│       │   ├── Message.jsx
│       │   └── ScoreCard.jsx
│       └── hooks/
│           ├── useChat.js
│           └── useScore.js
└── docs/
    ├── ARCHITECTURE.md
    ├── API.md
    └── DEPLOYMENT.md
```

---

## 👤 Team

- **Developer:** Alquama Shaibli
- **Hackathon:** FlowZint AI Hackathon 2026
- **Category:** Sales Bot

---

## 📄 License

MIT License — feel free to use and adapt.

---

*Built with ❤️ for FlowZint AI Hackathon 2026*
