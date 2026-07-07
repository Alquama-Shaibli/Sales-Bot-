# 📡 API Reference — EnterpriseLead AI

**Base URL (local):** `http://localhost:8000`  
**Base URL (production):** `https://your-app.railway.app`  
**Interactive Docs:** `{BASE_URL}/docs` (Swagger UI)

---

## Authentication

Currently open (no auth for hackathon MVP). Production should add `Authorization: Bearer <token>` header.

---

## Endpoints

### 🟢 Health

#### `GET /health`
Check if the API and database are operational.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "model": "claude-3-5-sonnet-20241022",
  "timestamp": "2026-07-04T12:00:00.000Z"
}
```

---

### 💬 Chat

#### `POST /api/conversation/start`
Start a new qualification conversation session.

**Response:**
```json
{
  "conversation_id": "uuid-string",
  "opening_message": "Hi! I'm your AI sales assistant..."
}
```

---

#### `POST /api/message`
Send a user message and receive the AI qualification question.

**Request:**
```json
{
  "user_message": "We're a 200-person B2B SaaS company using Salesforce.",
  "conversation_id": "uuid-string"
}
```

**Response:**
```json
{
  "response": "That's great! What specific pain points are you trying to solve?",
  "conversation_id": "uuid-string",
  "turn_count": 2
}
```

---

#### `POST /api/score`
Trigger AI scoring of the current conversation (available after 3+ turns).

**Request:**
```json
{
  "conversation_id": "uuid-string"
}
```

**Response:**
```json
{
  "overall_score": 87,
  "breakdown": {
    "icp_fit":        88,
    "intent_signals": 90,
    "timeline":       85,
    "authority":      92,
    "engagement":     80
  },
  "reasoning": "500-employee B2B SaaS with Q1 urgency, VP authority, $80k budget...",
  "recommendation": "Route immediately to senior AE."
}
```

---

### 🏆 Leads

#### `POST /api/lead/qualify`
Qualify the lead: create DB record, sync to HubSpot, send alert if hot.

**Request:**
```json
{
  "conversation_id": "uuid-string",
  "score": 87,
  "icp_fit": 90,
  "intent_level": "High",
  "email": "jane@acmecorp.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "company": "Acme Corp",
  "job_title": "CTO",
  "timeline": "Q1 2025"
}
```

**Response:**
```json
{
  "status": "hot",
  "lead_id": 42,
  "hubspot_contact_id": "123456789",
  "score": 87,
  "alert_sent": true,
  "message": "🔴 Hot lead! Routed to sales team."
}
```

**Status values:** `hot` (≥75) | `warm` (50-74) | `cold` (<50)

---

#### `GET /api/leads`
Get all qualified leads with optional filters.

**Query params:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `min_score` | int | — | Filter leads with score ≥ value |
| `status_filter` | string | — | `hot` \| `warm` \| `cold` |
| `limit` | int | 50 | Max results (max 200) |

**Example:** `GET /api/leads?status_filter=hot&min_score=80`

**Response:**
```json
{
  "total": 3,
  "leads": [
    {
      "id": 42,
      "email": "jane@acmecorp.com",
      "company": "Acme Corp",
      "score": 87,
      "status": "hot",
      "hubspot_id": "123456789",
      "hubspot_synced": true,
      "alert_sent": true,
      "created_at": "2026-07-04T12:00:00"
    }
  ]
}
```

---

#### `GET /api/leads/{lead_id}`
Get a single lead by ID.

**Response:** Full lead object including `first_name`, `last_name`, `job_title`, `icp_fit`, `intent_level`, `timeline`, `conversation_id`.

---

### 📊 Analytics

#### `GET /api/analytics/pipeline`
Full pipeline health snapshot.

**Response:**
```json
{
  "generated_at": "2026-07-04T12:00:00",
  "pipeline": {
    "total_leads": 47,
    "hot_leads": 12,
    "warm_leads": 21,
    "cold_leads": 14,
    "average_score": 63.4,
    "score_distribution": {"0-25": 5, "26-50": 9, "51-75": 21, "76-100": 12}
  },
  "integrations": {
    "hubspot_synced": 42,
    "hubspot_sync_rate": "89.4%",
    "alerts_sent": 12
  },
  "activity_24h": {
    "new_conversations": 18,
    "new_leads": 11,
    "conversions": 3,
    "conversion_rate": "16.7%"
  }
}
```

---

#### `GET /api/analytics/hot-leads`
All hot leads (score ≥ 75), sorted by score desc.

---

#### `GET /api/analytics/alerts-status`
Check which alert channels are configured.

**Response:**
```json
{
  "status": "ok",
  "channels": {
    "sms_enabled": true,
    "email_enabled": false,
    "threshold": 75
  },
  "message": "Alert system fully active ✅"
}
```

---

#### `GET /api/analytics/daily-metrics`
7-day breakdown of conversations, leads, and average score.

**Response:**
```json
{
  "days": 7,
  "metrics": [
    {"date": "2026-07-01", "day": "Tue", "conversations": 12, "leads_qualified": 8, "hot_leads": 2, "average_score": 67.5},
    {"date": "2026-07-02", "day": "Wed", "conversations": 15, "leads_qualified": 10, "hot_leads": 3, "average_score": 71.2}
  ]
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Conversation abc123 not found."
}
```

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad request (invalid UUID, invalid filter) |
| 404 | Resource not found |
| 500 | Internal server error |

---

## Rate Limits

- Claude API: 3 retries with exponential backoff (tenacity)
- HubSpot: 3 retries with exponential backoff (tenacity)
- No explicit rate limit on this API in MVP

---

*EnterpriseLead AI · FlowZint Hackathon 2026*
