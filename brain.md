# 🧠 BRAIN.MD — FlowZint Sales Bot: Live Build Tracker
> **Project:** EnterpriseLead AI | **Hackathon:** FlowZint 2026
> **Repo:** https://github.com/Alquama-Shaibli/Sales-Bot-.git
> **Deadline:** July 19, 2026 (11:59 PM)
> **Target:** 🥇 Gold Tier — ₹1,50,000 + Internship + 20,000 Credits

---

## 📍 CURRENT STATUS

```
▶ ACTIVE DAY   : Day 1 — Backend Foundation
✅ LAST FILE   : backend/routers/health.py
⏭ NEXT FILE   : backend/routers/chat.py
🔁 LAST COMMIT : "feat: add routers package + health check endpoint [Day 1]"
📦 COMMITS DONE: 3 of many
```

---

## 🗓️ MASTER PROGRESS TRACKER

### ✅ DAY 1 — Project Setup + Backend Foundation

#### 📁 Files Created
| # | File | Status | Commit |
|---|------|--------|--------|
| 1 | `.gitignore` | ✅ Done | Commit 1 |
| 2 | `README.md` | ✅ Done | Commit 1 |
| 3 | `backend/schemas.py` | ✅ Done | Commit 2 |
| 4 | `backend/main.py` | ✅ Done | Commit 2 |
| 5 | `backend/routers/__init__.py` | ✅ Done | Commit 3 |
| 6 | `backend/routers/health.py` | ✅ Done | Commit 3 |
| 7 | `backend/routers/chat.py` | 🟡 In Progress | — |
| 8 | `backend/routers/leads.py` | ⬜ Pending | — |
| 9 | `backend/requirements.txt` | ✅ Done | Pending commit |
| 10 | `backend/config.py` | ✅ Done | Pending commit |
| 11 | `backend/database.py` | ✅ Done | Pending commit |
| 12 | `backend/models.py` | ✅ Done | Pending commit |
| 13 | `backend/.env.example` | ✅ Done | Pending commit |
| 14 | `backend/Dockerfile` | ⬜ Pending | — |
| 15 | `backend/railway.toml` | ⬜ Pending | — |
| 16 | `backend/docker-compose.yml` | ⬜ Pending | — |
| 17 | `backend/services/__init__.py` | ⬜ Pending | — |
| 18 | `docs/ARCHITECTURE.md` | ⬜ Pending | — |

#### ✅ Day 1 Checklist
- [x] GitHub repo initialized & remote set
- [x] Project folder structure created
- [x] `requirements.txt` created
- [x] `config.py` — Pydantic Settings
- [x] `database.py` — PostgreSQL connection pool
- [x] `models.py` — 4 SQLAlchemy ORM tables
- [x] `schemas.py` — All Pydantic request/response models
- [x] `main.py` — FastAPI app with CORS, logging, lifespan
- [x] `routers/health.py` — Health check endpoint
- [ ] `routers/chat.py` — Chat endpoint skeletons
- [ ] `routers/leads.py` — Lead qualification endpoints
- [ ] `Dockerfile` + `railway.toml` + `docker-compose.yml`
- [ ] Push all remaining Day 1 files to GitHub

**Day 1 Status: 🟡 60% DONE**

---

### ⬜ DAY 2 — Claude Integration + Lead Scoring Engine

#### 📁 Files to Create
| # | File | Status |
|---|------|--------|
| 1 | `backend/services/__init__.py` | ⬜ |
| 2 | `backend/services/chat_service.py` | ⬜ |
| 3 | `backend/services/scoring_service.py` | ⬜ |
| 4 | Update `routers/chat.py` with real Claude logic | ⬜ |

#### Day 2 Checklist
- [ ] Claude API key in `.env`
- [ ] `ChatService` class — multi-turn conversation with Claude
- [ ] `ScoringService` class — 5-dimension lead scoring
- [ ] `POST /api/conversation/start` working
- [ ] `POST /api/message` working (saves to DB + Claude response)
- [ ] `POST /api/score` working (returns 0–100 + breakdown)
- [ ] Tested on 10 sample conversations

**Day 2 Status: ⬜ NOT STARTED**

---

### ⬜ DAY 3 — Database + Conversation Persistence

#### 📁 Files to Create
| # | File | Status |
|---|------|--------|
| 1 | `backend/crud.py` | ⬜ |
| 2 | `backend/repositories.py` | ⬜ |
| 3 | `backend/migrations/001_init.sql` | ⬜ |

#### Day 3 Checklist
- [ ] Full SQLAlchemy CRUD layer (`crud.py`)
- [ ] Repository pattern (`repositories.py`)
- [ ] DB indexes added
- [ ] Connection pooling tuned
- [ ] Reporting queries (high-value leads, by industry)
- [ ] 50+ test conversations run successfully

**Day 3 Status: ⬜ NOT STARTED**

---

### ⬜ DAY 4 — Frontend + Beautiful Chat UI

#### 📁 Files to Create
| # | File | Status |
|---|------|--------|
| 1 | `frontend/package.json` | ⬜ |
| 2 | `frontend/tailwind.config.js` | ⬜ |
| 3 | `frontend/src/App.jsx` | ⬜ |
| 4 | `frontend/src/components/ChatWidget.jsx` | ⬜ |
| 5 | `frontend/src/components/Message.jsx` | ⬜ |
| 6 | `frontend/src/components/ScoreCard.jsx` | ⬜ |
| 7 | `frontend/src/hooks/useChat.js` | ⬜ |
| 8 | `frontend/src/hooks/useScore.js` | ⬜ |
| 9 | `frontend/src/hooks/useApi.js` | ⬜ |
| 10 | `frontend/src/index.css` | ⬜ |

#### Day 4 Checklist
- [ ] React app initialized (`npx create-react-app`)
- [ ] TailwindCSS configured
- [ ] `ChatWidget.jsx` — Full chat interface
- [ ] `Message.jsx` — Message bubbles (user vs bot)
- [ ] `ScoreCard.jsx` — Score card with animated progress bars
- [ ] API hooks connected to backend
- [ ] Mobile responsive (tested on phone)
- [ ] No console errors

**Day 4 Status: ⬜ NOT STARTED**

---

### ⬜ DAY 5 — HubSpot Integration + CRM Sync

#### 📁 Files to Create
| # | File | Status |
|---|------|--------|
| 1 | `backend/services/hubspot_service.py` | ⬜ |
| 2 | `backend/services/alert_service.py` | ⬜ |
| 3 | Update `routers/leads.py` with HubSpot logic | ⬜ |

#### Day 5 Checklist
- [ ] HubSpot free account created (USER ACTION)
- [ ] Custom properties created in HubSpot
- [ ] `HubSpotClient` class
- [ ] `POST /api/lead/qualify` — creates contact + syncs score
- [ ] SMS alert for score > 75
- [ ] Email alert for score > 75
- [ ] End-to-end: chat → score → HubSpot

**Day 5 Status: ⬜ NOT STARTED**

---

### ⬜ DAY 6 — Testing + Polish + Optimization

#### 📁 Files to Create
| # | File | Status |
|---|------|--------|
| 1 | `backend/tests/test_chat.py` | ⬜ |
| 2 | `backend/tests/test_scoring.py` | ⬜ |
| 3 | `backend/tests/test_hubspot.py` | ⬜ |
| 4 | `docs/API.md` | ⬜ |
| 5 | `docs/ARCHITECTURE.md` | ⬜ |
| 6 | `docs/DEPLOYMENT.md` | ⬜ |

#### Day 6 Checklist
- [ ] All pytest tests passing
- [ ] API response < 2 seconds
- [ ] Score calculation < 3 seconds
- [ ] Frontend loads < 3 seconds
- [ ] 0 hardcoded secrets
- [ ] Security audit done
- [ ] All docs written

**Day 6 Status: ⬜ NOT STARTED**

---

### ⬜ DAY 7 — Final Deployment + Submission

#### Day 7 Checklist
- [ ] Railway production deployment verified
- [ ] All features working on live URL
- [ ] Demo video recorded (3–4 min)
- [ ] README.md polished with screenshots
- [ ] Submission form filled at flowzint.in
- [ ] **✅ SUBMITTED TO FLOWZINT**

**Day 7 Status: ⬜ NOT STARTED**

---

## 📁 PROJECT STRUCTURE (Live View)

```
Sales_bot/
├── brain.md                          ← 🧠 YOU ARE HERE
├── FlowZint_Sales_Bot_Complete_Guide.md
├── 7_Day_Build_Plan_With_AI_Prompts.md
├── Complete_7_Day_Build_Plan_EXTENDED.md
└── flowzint-sales-bot/               ← ACTUAL CODE REPO
    ├── .gitignore                    ✅
    ├── README.md                     ✅
    ├── backend/
    │   ├── main.py                   ✅
    │   ├── config.py                 ✅
    │   ├── database.py               ✅
    │   ├── models.py                 ✅
    │   ├── schemas.py                ✅
    │   ├── requirements.txt          ✅
    │   ├── .env.example              ✅
    │   ├── Dockerfile                ⬜
    │   ├── railway.toml              ⬜
    │   ├── docker-compose.yml        ⬜
    │   ├── routers/
    │   │   ├── __init__.py           ✅
    │   │   ├── health.py             ✅
    │   │   ├── chat.py               🟡 (next)
    │   │   └── leads.py              ⬜
    │   └── services/
    │       ├── __init__.py           ⬜ (Day 2)
    │       ├── chat_service.py       ⬜ (Day 2)
    │       ├── scoring_service.py    ⬜ (Day 2)
    │       └── hubspot_service.py    ⬜ (Day 5)
    ├── frontend/                     ⬜ (Day 4)
    └── docs/
        ├── ARCHITECTURE.md           ⬜ (Day 6)
        ├── API.md                    ⬜ (Day 6)
        └── DEPLOYMENT.md             ⬜ (Day 6)
```

---

## 🔑 API KEYS STATUS

| Key | Status | Notes |
|-----|--------|-------|
| `ANTHROPIC_API_KEY` | ⬜ USER MUST ADD | console.anthropic.com |
| `DATABASE_URL` | ⬜ USER MUST ADD | Railway or Supabase |
| `HUBSPOT_API_KEY` | ⬜ USER MUST ADD | Day 5 only |
| `TWILIO_*` | ⬜ Optional | SMS alerts |
| `SENDGRID_API_KEY` | ⬜ Optional | Email alerts |

---

## 📦 GIT COMMIT LOG

| # | Commit Message | Files | Status |
|---|---------------|-------|--------|
| 1 | `feat: add .gitignore and project README [Day 1]` | .gitignore, README.md | ✅ Pushed |
| 2 | `feat: add Pydantic schemas + FastAPI main app [Day 1]` | schemas.py, main.py | ✅ Pushed |
| 3 | `feat: add routers package + health check endpoint [Day 1]` | routers/__init__.py, health.py | ✅ Pushed |
| 4 | *Next commit* | chat.py, leads.py | 🟡 Upcoming |
| 5 | *Next commit* | requirements.txt, config.py, database.py, models.py | 🟡 Upcoming |

---

## 🚨 BLOCKERS & NOTES

- ⚠️ **User must add API keys** to `.env` before Day 2 can run
- ⚠️ **User must create HubSpot account** before Day 5
- ✅ Git remote set to: `https://github.com/Alquama-Shaibli/Sales-Bot-.git`
- ✅ Committing every 2 files as per user instruction
- 📝 brain.md gets updated after every commit

---

## 📊 OVERALL PROGRESS

```
Day 1 ████████████░░░░░░░░  60%
Day 2 ░░░░░░░░░░░░░░░░░░░░   0%
Day 3 ░░░░░░░░░░░░░░░░░░░░   0%
Day 4 ░░░░░░░░░░░░░░░░░░░░   0%
Day 5 ░░░░░░░░░░░░░░░░░░░░   0%
Day 6 ░░░░░░░░░░░░░░░░░░░░   0%
Day 7 ░░░░░░░░░░░░░░░░░░░░   0%

TOTAL ██░░░░░░░░░░░░░░░░░░   9%
```
