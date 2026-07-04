"""
crud.py — Database CRUD Operations
All Create, Read, Update, Delete operations for the 4 models.
Used by routers and services to interact with PostgreSQL.
"""
import logging
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import desc

from models import (
    Conversation, Message, Lead, LeadScore,
    ConversationStatus, MessageRole, LeadStatus
)

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════
#  CONVERSATION CRUD
# ════════════════════════════════════════════════════════════════

def create_conversation(db: Session) -> Conversation:
    """Create a new conversation and return it."""
    convo = Conversation(id=uuid.uuid4(), status=ConversationStatus.active)
    db.add(convo)
    db.commit()
    db.refresh(convo)
    logger.info(f"Created conversation: {convo.id}")
    return convo


def get_conversation(db: Session, conversation_id: str) -> Optional[Conversation]:
    """Fetch a conversation by UUID string."""
    try:
        cid = uuid.UUID(conversation_id)
        return db.query(Conversation).filter(Conversation.id == cid).first()
    except ValueError:
        return None


def get_all_conversations(db: Session, limit: int = 100) -> List[Conversation]:
    """Return all conversations, newest first."""
    return (
        db.query(Conversation)
        .order_by(desc(Conversation.created_at))
        .limit(limit)
        .all()
    )


def update_conversation_status(
    db: Session, conversation_id: str, status: ConversationStatus
) -> Optional[Conversation]:
    """Update conversation status."""
    convo = get_conversation(db, conversation_id)
    if convo:
        convo.status = status
        convo.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(convo)
    return convo


# ════════════════════════════════════════════════════════════════
#  MESSAGE CRUD
# ════════════════════════════════════════════════════════════════

def add_message(
    db: Session,
    conversation_id: str,
    role: MessageRole,
    content: str,
) -> Optional[Message]:
    """Add a message to a conversation."""
    try:
        cid = uuid.UUID(conversation_id)
        msg = Message(conversation_id=cid, role=role, content=content)
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to add message: {e}")
        return None


def get_messages(db: Session, conversation_id: str) -> List[Message]:
    """Return all messages for a conversation, ordered by time."""
    try:
        cid = uuid.UUID(conversation_id)
        return (
            db.query(Message)
            .filter(Message.conversation_id == cid)
            .order_by(Message.created_at.asc())
            .all()
        )
    except ValueError:
        return []


def get_message_count(db: Session, conversation_id: str) -> int:
    """Count messages in a conversation."""
    try:
        cid = uuid.UUID(conversation_id)
        return db.query(Message).filter(Message.conversation_id == cid).count()
    except ValueError:
        return 0


def get_user_turn_count(db: Session, conversation_id: str) -> int:
    """Count only user messages (turns) in a conversation."""
    try:
        cid = uuid.UUID(conversation_id)
        return (
            db.query(Message)
            .filter(
                Message.conversation_id == cid,
                Message.role == MessageRole.user,
            )
            .count()
        )
    except ValueError:
        return 0


# ════════════════════════════════════════════════════════════════
#  LEAD CRUD
# ════════════════════════════════════════════════════════════════

def create_lead(db: Session, conversation_id: str, lead_data: Dict[str, Any]) -> Optional[Lead]:
    """Create a new lead from qualification data."""
    try:
        cid = uuid.UUID(conversation_id)
        score = lead_data.get("score", 0)

        if score >= 75:
            status = LeadStatus.hot
        elif score >= 50:
            status = LeadStatus.warm
        else:
            status = LeadStatus.cold

        lead = Lead(
            conversation_id=cid,
            email=lead_data.get("email"),
            first_name=lead_data.get("first_name"),
            last_name=lead_data.get("last_name"),
            company=lead_data.get("company"),
            job_title=lead_data.get("job_title"),
            score=score,
            icp_fit=lead_data.get("icp_fit", 0),
            intent_level=lead_data.get("intent_level"),
            timeline=lead_data.get("timeline"),
            status=status,
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
        logger.info(f"Created lead: {lead.email} | score={lead.score}")
        return lead
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create lead: {e}")
        return None


def get_lead(db: Session, lead_id: int) -> Optional[Lead]:
    """Get a lead by integer ID."""
    return db.query(Lead).filter(Lead.id == lead_id).first()


def get_lead_by_email(db: Session, email: str) -> Optional[Lead]:
    """Look up a lead by email address."""
    return db.query(Lead).filter(Lead.email == email).first()


def get_lead_by_conversation(db: Session, conversation_id: str) -> Optional[Lead]:
    """Get the lead associated with a conversation."""
    try:
        cid = uuid.UUID(conversation_id)
        return db.query(Lead).filter(Lead.conversation_id == cid).first()
    except ValueError:
        return None


def get_high_value_leads(db: Session, threshold: int = 75, limit: int = 100) -> List[Lead]:
    """Return all leads scoring above the threshold."""
    return (
        db.query(Lead)
        .filter(Lead.score >= threshold)
        .order_by(desc(Lead.score))
        .limit(limit)
        .all()
    )


def update_lead_hubspot(db: Session, lead_id: int, hubspot_id: str) -> Optional[Lead]:
    """Mark a lead as synced with HubSpot."""
    lead = get_lead(db, lead_id)
    if lead:
        lead.hubspot_id = hubspot_id
        lead.hubspot_synced = True
        lead.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(lead)
    return lead


def mark_alert_sent(db: Session, lead_id: int) -> Optional[Lead]:
    """Mark that an alert has been sent for this lead."""
    lead = get_lead(db, lead_id)
    if lead:
        lead.alert_sent = True
        lead.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(lead)
    return lead


# ════════════════════════════════════════════════════════════════
#  LEAD SCORE CRUD
# ════════════════════════════════════════════════════════════════

def save_lead_score(db: Session, conversation_id: str, score_data: Dict[str, Any]) -> Optional[LeadScore]:
    """Persist a score record for a conversation."""
    try:
        cid = uuid.UUID(conversation_id)
        overall = score_data.get("overall_score", 0)

        if overall >= 75:
            recommendation = "route_to_sales"
        elif overall >= 50:
            recommendation = "nurture"
        else:
            recommendation = "marketing_only"

        ls = LeadScore(
            conversation_id=cid,
            overall_score=overall,
            icp_fit=score_data.get("icp_fit", 0),
            intent_signals=score_data.get("intent_signals", 0),
            timeline=score_data.get("timeline", 0),
            authority=score_data.get("authority", 0),
            engagement=score_data.get("engagement", 0),
            reasoning=score_data.get("reasoning", ""),
            recommendation=recommendation,
        )
        db.add(ls)
        db.commit()
        db.refresh(ls)
        logger.info(f"Saved lead score: {overall}/100 for conv {conversation_id}")
        return ls
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save lead score: {e}")
        return None


def get_latest_score(db: Session, conversation_id: str) -> Optional[LeadScore]:
    """Get the most recent score for a conversation."""
    try:
        cid = uuid.UUID(conversation_id)
        return (
            db.query(LeadScore)
            .filter(LeadScore.conversation_id == cid)
            .order_by(desc(LeadScore.created_at))
            .first()
        )
    except ValueError:
        return None


def get_score_history(db: Session, conversation_id: str) -> List[LeadScore]:
    """Return all scoring attempts for a conversation."""
    try:
        cid = uuid.UUID(conversation_id)
        return (
            db.query(LeadScore)
            .filter(LeadScore.conversation_id == cid)
            .order_by(desc(LeadScore.created_at))
            .all()
        )
    except ValueError:
        return []
