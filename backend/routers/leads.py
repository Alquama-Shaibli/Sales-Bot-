"""
routers/leads.py — Lead Qualification & CRM Sync Endpoints
Handles lead creation, HubSpot sync, and high-value lead queries.
HubSpot logic delegated to services/hubspot_service.py (Day 5).
"""
import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from database import get_db
from schemas import LeadQualifyRequest, LeadQualifyResponse
from models import Lead, Conversation, ConversationStatus, LeadStatus, IntentLevel

router = APIRouter()
logger = logging.getLogger(__name__)


# ── POST /api/lead/qualify ────────────────────────────────────────────────────
@router.post(
    "/lead/qualify",
    response_model=LeadQualifyResponse,
    summary="Qualify a lead and sync to HubSpot CRM",
)
async def qualify_lead(request: LeadQualifyRequest, db: Session = Depends(get_db)):
    """
    After a conversation is scored, call this endpoint to:
    1. Create/update the lead record in local DB
    2. Sync to HubSpot CRM (Day 5)
    3. Send SMS/email alert if score > 75 (Day 5)
    4. Return the lead ID and HubSpot contact ID
    """
    try:
        # Validate conversation exists
        convo = db.query(Conversation).filter(
            Conversation.id == uuid.UUID(request.conversation_id)
        ).first()

        if not convo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {request.conversation_id} not found.",
            )

        # Check if lead already exists for this conversation
        existing_lead = db.query(Lead).filter(
            Lead.conversation_id == convo.id
        ).first()

        # Determine lead status from score
        if request.score >= 75:
            lead_status = LeadStatus.hot
        elif request.score >= 50:
            lead_status = LeadStatus.warm
        else:
            lead_status = LeadStatus.cold

        # Determine intent level
        intent = None
        if request.intent_level:
            try:
                intent = IntentLevel(request.intent_level.value)
            except Exception:
                intent = None

        hubspot_id = None
        alert_sent = False

        if existing_lead:
            # Update existing lead
            existing_lead.email = request.email or existing_lead.email
            existing_lead.first_name = request.first_name or existing_lead.first_name
            existing_lead.last_name = request.last_name or existing_lead.last_name
            existing_lead.company = request.company or existing_lead.company
            existing_lead.job_title = request.job_title or existing_lead.job_title
            existing_lead.score = request.score
            existing_lead.icp_fit = request.icp_fit
            existing_lead.intent_level = intent
            existing_lead.timeline = request.timeline
            existing_lead.status = lead_status
            existing_lead.updated_at = datetime.utcnow()
            db.flush()
            lead = existing_lead
        else:
            # Create new lead
            lead = Lead(
                conversation_id=convo.id,
                email=request.email,
                first_name=request.first_name,
                last_name=request.last_name,
                company=request.company,
                job_title=request.job_title,
                score=request.score,
                icp_fit=request.icp_fit,
                intent_level=intent,
                timeline=request.timeline,
                status=lead_status,
            )
            db.add(lead)
            db.flush()

        # ── HubSpot Sync (Day 5) ──────────────────────────────────────────
        try:
            from services.hubspot_service import HubSpotService
            hs_service = HubSpotService()
            hubspot_id = await hs_service.sync_lead(lead, request)
            lead.hubspot_id = hubspot_id
            lead.hubspot_synced = True
            logger.info(f"✅ Lead synced to HubSpot: {hubspot_id}")
        except ImportError:
            logger.info("HubSpot service not yet active (Day 5)")
        except Exception as e:
            logger.error(f"HubSpot sync failed (non-blocking): {e}")

        # ── Alert System (Day 5) ──────────────────────────────────────────
        if request.score >= 75:
            try:
                from services.alert_service import AlertService
                alert_svc = AlertService()
                await alert_svc.send_hot_lead_alert(lead)
                lead.alert_sent = True
                alert_sent = True
                logger.info(f"🔔 Hot lead alert sent for score {request.score}")
            except ImportError:
                logger.info("Alert service not yet active (Day 5)")
            except Exception as e:
                logger.error(f"Alert send failed (non-blocking): {e}")

        # Mark conversation as converted if hot lead
        if lead_status == LeadStatus.hot:
            convo.status = ConversationStatus.converted

        db.commit()

        status_msg = {
            "hot": "🔴 Hot lead! Routed to sales team.",
            "warm": "🟡 Warm lead added to nurture sequence.",
            "cold": "🔵 Cold lead added to marketing list.",
        }

        logger.info(
            f"Lead qualified: {request.email} | Score: {request.score} | "
            f"Status: {lead_status.value} | HubSpot: {hubspot_id}"
        )

        return LeadQualifyResponse(
            status=lead_status.value,
            lead_id=lead.id,
            hubspot_contact_id=hubspot_id,
            score=request.score,
            alert_sent=alert_sent,
            message=status_msg.get(lead_status.value, "Lead qualified."),
        )

    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation_id format.",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Lead qualification error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to qualify lead.",
        )


# ── GET /api/leads ────────────────────────────────────────────────────────────
@router.get(
    "/leads",
    summary="Get all qualified leads (with optional filters)",
)
async def get_leads(
    min_score: Optional[int] = Query(default=None, ge=0, le=100, description="Minimum lead score"),
    status_filter: Optional[str] = Query(default=None, description="hot | warm | cold"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    Returns all qualified leads.
    Filter by score threshold or status.
    Used by sales team dashboard.
    """
    try:
        query = db.query(Lead)

        if min_score is not None:
            query = query.filter(Lead.score >= min_score)

        if status_filter:
            try:
                s = LeadStatus(status_filter)
                query = query.filter(Lead.status == s)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="status_filter must be: hot, warm, or cold",
                )

        leads = query.order_by(Lead.score.desc()).limit(limit).all()

        return {
            "total": len(leads),
            "leads": [
                {
                    "id": l.id,
                    "email": l.email,
                    "company": l.company,
                    "score": l.score,
                    "status": l.status.value if l.status else None,
                    "icp_fit": l.icp_fit,
                    "intent_level": l.intent_level.value if l.intent_level else None,
                    "timeline": l.timeline,
                    "hubspot_id": l.hubspot_id,
                    "hubspot_synced": l.hubspot_synced,
                    "alert_sent": l.alert_sent,
                    "created_at": l.created_at.isoformat() if l.created_at else None,
                }
                for l in leads
            ],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get leads error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve leads.",
        )


# ── GET /api/leads/{lead_id} ──────────────────────────────────────────────────
@router.get(
    "/leads/{lead_id}",
    summary="Get a specific lead by ID",
)
async def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """Returns a single lead record."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead {lead_id} not found.",
        )
    return {
        "id": lead.id,
        "email": lead.email,
        "first_name": lead.first_name,
        "last_name": lead.last_name,
        "company": lead.company,
        "job_title": lead.job_title,
        "score": lead.score,
        "status": lead.status.value if lead.status else None,
        "icp_fit": lead.icp_fit,
        "intent_level": lead.intent_level.value if lead.intent_level else None,
        "timeline": lead.timeline,
        "hubspot_id": lead.hubspot_id,
        "hubspot_synced": lead.hubspot_synced,
        "alert_sent": lead.alert_sent,
        "conversation_id": str(lead.conversation_id),
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
    }
