"""
routers/analytics.py — Pipeline Analytics & Dashboard Endpoints
Provides real-time metrics for the sales team dashboard.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from database import get_db
from models import Lead, LeadScore, Conversation, ConversationStatus, LeadStatus
from services.alert_service import AlertService

router = APIRouter()
logger = logging.getLogger(__name__)


# ── GET /api/analytics/pipeline ───────────────────────────────────────────────
@router.get(
    "/analytics/pipeline",
    summary="Get full pipeline health snapshot",
)
async def get_pipeline(db: Session = Depends(get_db)):
    """
    Returns a comprehensive pipeline snapshot:
    - Lead counts by status (hot / warm / cold)
    - Average score and score distribution
    - HubSpot sync rate
    - Alert coverage
    - Conversion rate (last 24h vs all time)
    """
    try:
        total_leads     = db.query(Lead).count()
        hot_leads       = db.query(Lead).filter(Lead.status == LeadStatus.hot).count()
        warm_leads      = db.query(Lead).filter(Lead.status == LeadStatus.warm).count()
        cold_leads      = db.query(Lead).filter(Lead.status == LeadStatus.cold).count()
        avg_score_raw   = db.query(func.avg(Lead.score)).scalar() or 0
        avg_score       = round(float(avg_score_raw), 1)
        synced          = db.query(Lead).filter(Lead.hubspot_synced.is_(True)).count()
        alerts_sent     = db.query(Lead).filter(Lead.alert_sent.is_(True)).count()

        # 24h activity
        since_24h = datetime.utcnow() - timedelta(hours=24)
        new_leads_24h   = db.query(Lead).filter(Lead.created_at >= since_24h).count()
        new_convos_24h  = db.query(Conversation).filter(Conversation.created_at >= since_24h).count()
        converted_24h   = db.query(Conversation).filter(
            Conversation.status == ConversationStatus.converted,
            Conversation.updated_at >= since_24h,
        ).count()

        # Score buckets
        all_scores = [row[0] for row in db.query(Lead.score).all()]
        buckets = {"0-25": 0, "26-50": 0, "51-75": 0, "76-100": 0}
        for s in all_scores:
            if s <= 25:   buckets["0-25"] += 1
            elif s <= 50: buckets["26-50"] += 1
            elif s <= 75: buckets["51-75"] += 1
            else:         buckets["76-100"] += 1

        # Rates
        sync_rate       = round((synced / total_leads * 100), 1) if total_leads else 0
        conversion_rate = round((converted_24h / new_convos_24h * 100), 1) if new_convos_24h else 0

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "pipeline": {
                "total_leads":    total_leads,
                "hot_leads":      hot_leads,
                "warm_leads":     warm_leads,
                "cold_leads":     cold_leads,
                "average_score":  avg_score,
                "score_distribution": buckets,
            },
            "integrations": {
                "hubspot_synced":      synced,
                "hubspot_sync_rate":   f"{sync_rate}%",
                "alerts_sent":         alerts_sent,
            },
            "activity_24h": {
                "new_conversations":   new_convos_24h,
                "new_leads":           new_leads_24h,
                "conversions":         converted_24h,
                "conversion_rate":     f"{conversion_rate}%",
            },
        }

    except Exception as e:
        logger.error(f"Pipeline analytics error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute pipeline metrics.",
        )


# ── GET /api/analytics/hot-leads ──────────────────────────────────────────────
@router.get(
    "/analytics/hot-leads",
    summary="Get all hot leads (score ≥ 75), newest first",
)
async def get_hot_leads(db: Session = Depends(get_db)):
    """
    Returns all hot leads sorted by score descending.
    Used by the sales team for immediate follow-up.
    """
    try:
        leads = (
            db.query(Lead)
            .filter(Lead.status == LeadStatus.hot)
            .order_by(Lead.score.desc())
            .all()
        )

        return {
            "count": len(leads),
            "hot_leads": [
                {
                    "id":            l.id,
                    "email":         l.email,
                    "first_name":    l.first_name,
                    "last_name":     l.last_name,
                    "company":       l.company,
                    "job_title":     l.job_title,
                    "score":         l.score,
                    "timeline":      l.timeline,
                    "hubspot_id":    l.hubspot_id,
                    "hubspot_synced":l.hubspot_synced,
                    "alert_sent":    l.alert_sent,
                    "qualified_at":  l.created_at.isoformat() if l.created_at else None,
                }
                for l in leads
            ],
        }

    except Exception as e:
        logger.error(f"Hot leads error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve hot leads.",
        )


# ── GET /api/analytics/alerts-status ──────────────────────────────────────────
@router.get(
    "/analytics/alerts-status",
    summary="Check which alert channels are active",
)
async def get_alerts_status():
    """
    Returns which alert channels (SMS/email) are configured and ready.
    Useful for admin health check.
    """
    try:
        svc = AlertService()
        return {
            "status": "ok",
            "channels": svc.is_configured(),
            "message": (
                "Alert system fully active ✅"
                if svc.sms.enabled or svc.email.enabled
                else "⚠️ No alert channels configured. Set TWILIO_* or SENDGRID_* env vars."
            ),
        }
    except Exception as e:
        logger.error(f"Alerts status error: {e}", exc_info=True)
        return {"status": "error", "detail": str(e)}


# ── GET /api/analytics/daily-metrics ──────────────────────────────────────────
@router.get(
    "/analytics/daily-metrics",
    summary="Get daily conversation and lead metrics for the last 7 days",
)
async def get_daily_metrics(db: Session = Depends(get_db)):
    """
    Returns day-by-day breakdown for the past 7 days:
    conversations started, leads qualified, average score.
    """
    try:
        rows = []
        for days_ago in range(6, -1, -1):
            day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_ago)
            day_end   = day_start + timedelta(days=1)

            convos = db.query(Conversation).filter(
                Conversation.created_at >= day_start,
                Conversation.created_at < day_end,
            ).count()

            leads_q = db.query(Lead).filter(
                Lead.created_at >= day_start,
                Lead.created_at < day_end,
            )
            leads_count = leads_q.count()
            avg_s = db.query(func.avg(Lead.score)).filter(
                Lead.created_at >= day_start,
                Lead.created_at < day_end,
            ).scalar() or 0

            hot_count = leads_q.filter(Lead.status == LeadStatus.hot).count()

            rows.append({
                "date":            day_start.strftime("%Y-%m-%d"),
                "day":             day_start.strftime("%a"),
                "conversations":   convos,
                "leads_qualified": leads_count,
                "hot_leads":       hot_count,
                "average_score":   round(float(avg_s), 1),
            })

        return {"days": 7, "metrics": rows}

    except Exception as e:
        logger.error(f"Daily metrics error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute daily metrics.",
        )
