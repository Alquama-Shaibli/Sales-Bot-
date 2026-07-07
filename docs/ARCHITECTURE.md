# 🏗️ Architecture — EnterpriseLead AI

> **FlowZint Hackathon 2026** | B2B SaaS Lead Qualification Agent

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ENTERPRISE LEAD AI                           │
│                  B2B Lead Qualification Platform                    │
└─────────────────────────────────────────────────────────────────────┘

 Browser (React)          Backend (FastAPI)           External APIs
 ──────────────           ─────────────────           ─────────────
 ┌────────────┐           ┌───────────────┐           ┌───────────┐
 │ ChatWidget │◄─ REST ──►│ /api/message  │◄─────────►│  Claude   │
 │ ScoreCard  │           │ /api/score    │           │  Sonnet   │
 │ App.jsx    │           │ /api/lead/    │           └───────────┘
 └────────────┘           │   qualify     │
                          │ /api/analytics│           ┌───────────┐
                          └──────┬────────┘           │  HubSpot  │
                                 │                    │   CRM     │
                          ┌──────▼────────┐           └───────────┘
                          │  PostgreSQL   │
                          │  Database     │           ┌───────────┐
                          └───────────────┘           │  Twilio   │
                                                      │  SendGrid │
                                                      └───────────┘
```

---

## Layer Architecture

### 1. Frontend — React SPA

| Component | Purpose |
|-----------|---------|
| `App.jsx` | Root layout: header, sidebar, footer |
| `ChatWidget.jsx` | Multi-turn chat interface, score reveal panel |
| `Message.jsx` | Animated message bubble (user/bot) |
| `ScoreCard.jsx` | 5-dim animated score circle + bar chart |
| `LoadingIndicator.jsx` | Pulsing 3-dot typing animation |
| `useChat.js` | Chat state: sessions, messages, turns, errors |
| `useScore.js` | Score state: scoring trigger, CRM qualify |
| `useApi.js` | Axios client with error normalization |

### 2. Backend — FastAPI

```
backend/
├── main.py              ← App factory, CORS, router mounting
├── config.py            ← Pydantic settings (env vars)
├── database.py          ← SQLAlchemy engine, session factory
├── models.py            ← ORM models (Conversation, Message, Lead, LeadScore)
├── schemas.py           ← Pydantic request/response schemas
├── crud.py              ← Low-level DB operations
├── repositories.py      ← Repository pattern over crud.py
├── routers/
│   ├── health.py        ← GET /health
│   ├── chat.py          ← POST /api/conversation/start, /api/message, /api/score
│   ├── leads.py         ← POST /api/lead/qualify, GET /api/leads
│   └── analytics.py     ← GET /api/analytics/*
└── services/
    ├── chat_service.py      ← Claude API integration (multi-turn)
    ├── scoring_service.py   ← 5-dimension scoring engine
    ├── hubspot_service.py   ← HubSpot CRM sync (create-or-update)
    └── alert_service.py     ← Twilio SMS + SendGrid email alerts
```

### 3. Database — PostgreSQL

```sql
conversations ─┐
               ├── messages       (chat history)
               └── leads ─────── lead_scores
```

| Table | Purpose |
|-------|---------|
| `conversations` | Session tracking, status, turn count |
| `messages` | Full chat transcript per conversation |
| `leads` | Qualified lead records with CRM sync status |
| `lead_scores` | Score snapshots per dimension per conversation |

---

## Data Flow — Full Qualification Journey

```
1. User opens React app
   └── GET /health (readiness check)

2. Click "Start Conversation"
   └── POST /api/conversation/start
       → Creates Conversation row (status=active)
       → Returns opening_message from ChatService

3. Multi-turn chat (up to N exchanges)
   └── POST /api/message
       └── ChatService.send_message(history)
           → Anthropic Claude claude-3-5-sonnet-20241022
           → Returns next qualifying question
           → Message saved to DB

4. Score button appears (after 3+ turns)
   └── POST /api/score
       └── ScoringService.score_conversation(transcript)
           → Claude analyzes full transcript
           → Returns JSON: {overall_score, breakdown, reasoning}
           → LeadScore row created

5. "Route to Sales" / Qualify button
   └── POST /api/lead/qualify
       ├── Lead upserted in DB (hot/warm/cold status)
       ├── HubSpotService.sync_lead() → CRM contact created
       └── If score ≥ 75 → AlertService.send_hot_lead_alert()
                           ├── Twilio SMS to sales phone
                           └── SendGrid email with HTML breakdown

6. Analytics dashboard
   └── GET /api/analytics/pipeline
   └── GET /api/analytics/hot-leads
   └── GET /api/analytics/daily-metrics
```

---

## Scoring Engine — 5 Dimensions

| Dimension | Weight | Signals Evaluated |
|-----------|--------|-------------------|
| **ICP Fit** | 30% | Company size, industry, tech stack, Salesforce/HubSpot user |
| **Intent Signals** | 25% | Pain point articulation, urgency language, demo requests |
| **Timeline** | 20% | Specific quarter/month, "already evaluated" competitors |
| **Authority** | 15% | Job title (VP/C-suite = high), decision-making power |
| **Engagement** | 10% | Message length, follow-up questions, detail provided |

**Scoring Formula:**
```
overall_score = 0.30 × icp_fit
              + 0.25 × intent_signals
              + 0.20 × timeline
              + 0.15 × authority
              + 0.10 × engagement
```

**Lead Routing:**
- 🔴 **75-100** → Hot Lead → AE + SMS/email alert + HubSpot "Hot Lead" stage
- 🟡 **50-74** → Warm Lead → HubSpot "Marketing Qualified" stage
- 🔵 **0-49** → Cold Lead → HubSpot "Awareness" stage

---

## Infrastructure

### Railway Deployment (Backend)
- **Plan:** Hobby ($5/month)
- **PostgreSQL:** Railway managed Postgres
- **Env vars:** Set via Railway dashboard
- **Auto-deploy:** Push to `master` → Railway deploys

### Vercel Deployment (Frontend)
- **Build cmd:** `npm run build`
- **Output dir:** `build/`
- **Env:** `REACT_APP_API_URL=https://your-backend.railway.app`

### Local Development
```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend && npm install && npm start
```

---

## Security Considerations

| Concern | Mitigation |
|---------|-----------|
| API key exposure | Env vars only, never committed |
| SQL injection | SQLAlchemy ORM parameterized queries |
| CORS | Whitelist-only origins in `main.py` |
| Rate limiting | Tenacity retry on Claude + HubSpot |
| PII handling | Email stored only on explicit qualify action |

---

*Generated: FlowZint Hackathon 2026 | EnterpriseLead AI Team*
