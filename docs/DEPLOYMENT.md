# 🚀 Deployment Guide — EnterpriseLead AI

> Complete deployment guide for Railway (backend) + Vercel (frontend)

---

## Prerequisites

- [x] GitHub account with this repo pushed
- [x] [Railway](https://railway.app) account (free tier works)
- [x] [Vercel](https://vercel.com) account (free tier works)
- [x] Anthropic API key from [console.anthropic.com](https://console.anthropic.com)
- [ ] Optional: HubSpot Private App key
- [ ] Optional: Twilio + SendGrid accounts for alerts

---

## Step 1 — Deploy Backend on Railway

### 1.1 Create Railway Project

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# From repo root
railway init
railway up
```

**OR use Railway Dashboard:**
1. Go to [railway.app](https://railway.app) → **New Project**
2. Select **Deploy from GitHub repo**
3. Select `Sales-Bot-` → set **Root Directory** to `backend`

### 1.2 Add PostgreSQL

In Railway project dashboard:
1. Click **+ New Service** → **Database** → **PostgreSQL**
2. Railway auto-sets `DATABASE_URL` in your backend service ✅

### 1.3 Set Environment Variables

In Railway → **Variables** tab, add:

```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
DEBUG=False
ENVIRONMENT=production
PORT=8000

# Optional — Alert system
HUBSPOT_API_KEY=pat-na1-xxxxx
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_FROM=+1XXXXXXXXXX
SALES_ALERT_PHONE=+91XXXXXXXXXX
SENDGRID_API_KEY=SG.xxxxx
SALES_EMAIL=sales@yourcompany.com
LEAD_SCORE_THRESHOLD=75
```

### 1.4 Configure Railway Deploy

Railway auto-detects the `Dockerfile` in `backend/`. No extra config needed.

Your backend will be live at: `https://your-app-name.railway.app`

**Verify:** `curl https://your-app-name.railway.app/health`

---

## Step 2 — Deploy Frontend on Vercel

### 2.1 Create Vercel Project

```bash
# Install Vercel CLI
npm install -g vercel

# From repo root
cd frontend
vercel
```

**OR use Vercel Dashboard:**
1. Go to [vercel.com](https://vercel.com) → **Add New Project**
2. Import `Sales-Bot-` GitHub repo
3. Set **Root Directory** to `frontend`
4. Set **Framework** to `Create React App`

### 2.2 Set Environment Variable

In Vercel project → **Settings** → **Environment Variables**:

```
REACT_APP_API_URL=https://your-app-name.railway.app
```

### 2.3 Deploy

```bash
vercel --prod
```

Frontend will be live at: `https://your-frontend.vercel.app`

---

## Step 3 — Database Migration

After Railway deploys, run the SQL migration:

```bash
# Get connection string from Railway
railway connect postgresql

# Run migration
psql $DATABASE_URL < backend/migrations/001_init.sql
```

**OR** — The app auto-creates tables on startup via SQLAlchemy (`create_tables()` in `main.py`). The SQL migration adds indexes and views for performance.

---

## Step 4 — Verify Deployment

```bash
# Backend health
curl https://your-app.railway.app/health

# Start a conversation
curl -X POST https://your-app.railway.app/api/conversation/start

# Check analytics
curl https://your-app.railway.app/api/analytics/pipeline
```

Open the Swagger docs: `https://your-app.railway.app/docs`

---

## Local Development

```bash
# 1. Clone repo
git clone https://github.com/Alquama-Shaibli/Sales-Bot-.git
cd Sales-Bot-

# 2. Backend setup
cd backend
cp .env.example .env
# Edit .env — add ANTHROPIC_API_KEY + DATABASE_URL

pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 3. Frontend setup (new terminal)
cd frontend
npm install
REACT_APP_API_URL=http://localhost:8000 npm start
```

### With Docker Compose (full stack)

```bash
# From repo root
docker-compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# PostgreSQL: localhost:5432
```

---

## Running Tests

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific suite
pytest tests/test_scoring.py -v
pytest tests/test_chat.py -v
pytest tests/test_hubspot.py -v

# With coverage
pip install pytest-cov
pytest tests/ --cov=. --cov-report=html
```

---

## Monitoring & Logs

### Railway Logs
```bash
railway logs --tail
```

### Key Log Messages to Watch
```
✅ Database ready                  ← Startup OK
✅ Lead synced to HubSpot: 1234    ← CRM working
🔔 Hot lead alert sent             ← Alerts working
❌ Database startup failed          ← Check DATABASE_URL
```

---

## Cost Estimate (Production)

| Service | Plan | Monthly Cost |
|---------|------|-------------|
| Railway Backend | Hobby | ~$5 |
| Railway PostgreSQL | Hobby | ~$5 |
| Vercel Frontend | Free | $0 |
| Anthropic Claude | Pay-per-use | ~$10-50 |
| Twilio SMS | Pay-per-use | ~$1/month |
| SendGrid Email | Free tier | $0 |
| **Total** | | **~$21-61/month** |

---

## Troubleshooting

| Problem | Solution |
|---------|---------|
| `DATABASE_URL not set` | Add variable in Railway dashboard |
| `ANTHROPIC_API_KEY not found` | Add to Railway env vars |
| CORS errors from frontend | Add Vercel URL to `allow_origins` in `main.py` |
| `502 Bad Gateway` | Check Railway logs — likely DB connection issue |
| HubSpot sync fails | Verify `HUBSPOT_API_KEY` is a Private App token, not OAuth |
| SMS not sending | Verify Twilio phone numbers are verified in Twilio console |

---

*EnterpriseLead AI · FlowZint Hackathon 2026*
