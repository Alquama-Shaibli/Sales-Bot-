"""
repositories.py — Repository Pattern for Data Access
Clean abstraction over CRUD operations.
Each repository wraps DB access for a single model.
"""
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

import crud
from models import (
    Conversation, Message, Lead, LeadScore,
    ConversationStatus, MessageRole
)

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════
#  CONVERSATION REPOSITORY
# ════════════════════════════════════════════════════════════════

class ConversationRepository:
    """Handles all DB operations for Conversation model."""

    def __init__(self, db: Session):
        self.db = db

    def create(self) -> Conversation:
        return crud.create_conversation(self.db)

    def get(self, conversation_id: str) -> Optional[Conversation]:
        return crud.get_conversation(self.db, conversation_id)

    def get_or_404(self, conversation_id: str) -> Conversation:
        convo = self.get(conversation_id)
        if not convo:
            raise ValueError(f"Conversation {conversation_id} not found")
        return convo

    def list_all(self, limit: int = 100) -> List[Conversation]:
        return crud.get_all_conversations(self.db, limit)

    def set_status(self, conversation_id: str, status: ConversationStatus) -> Optional[Conversation]:
        return crud.update_conversation_status(self.db, conversation_id, status)

    def mark_completed(self, conversation_id: str) -> Optional[Conversation]:
        return self.set_status(conversation_id, ConversationStatus.completed)

    def mark_converted(self, conversation_id: str) -> Optional[Conversation]:
        return self.set_status(conversation_id, ConversationStatus.converted)

    def mark_abandoned(self, conversation_id: str) -> Optional[Conversation]:
        return self.set_status(conversation_id, ConversationStatus.abandoned)


# ════════════════════════════════════════════════════════════════
#  MESSAGE REPOSITORY
# ════════════════════════════════════════════════════════════════

class MessageRepository:
    """Handles all DB operations for Message model."""

    def __init__(self, db: Session):
        self.db = db

    def add_user_message(self, conversation_id: str, content: str) -> Optional[Message]:
        return crud.add_message(self.db, conversation_id, MessageRole.user, content)

    def add_bot_message(self, conversation_id: str, content: str) -> Optional[Message]:
        return crud.add_message(self.db, conversation_id, MessageRole.assistant, content)

    def get_all(self, conversation_id: str) -> List[Message]:
        return crud.get_messages(self.db, conversation_id)

    def count(self, conversation_id: str) -> int:
        return crud.get_message_count(self.db, conversation_id)

    def user_turn_count(self, conversation_id: str) -> int:
        return crud.get_user_turn_count(self.db, conversation_id)

    def get_formatted_for_claude(self, conversation_id: str) -> List[Dict[str, str]]:
        """
        Return messages formatted as Claude API expects:
        [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
        """
        messages = self.get_all(conversation_id)
        return [
            {
                "role": m.role.value if hasattr(m.role, "value") else str(m.role),
                "content": m.content,
            }
            for m in messages
            if (m.role.value if hasattr(m.role, "value") else str(m.role)) in ("user", "assistant")
        ]


# ════════════════════════════════════════════════════════════════
#  LEAD REPOSITORY
# ════════════════════════════════════════════════════════════════

class LeadRepository:
    """Handles all DB operations for Lead model."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, conversation_id: str, lead_data: Dict[str, Any]) -> Optional[Lead]:
        return crud.create_lead(self.db, conversation_id, lead_data)

    def get(self, lead_id: int) -> Optional[Lead]:
        return crud.get_lead(self.db, lead_id)

    def find_by_email(self, email: str) -> Optional[Lead]:
        return crud.get_lead_by_email(self.db, email)

    def find_by_conversation(self, conversation_id: str) -> Optional[Lead]:
        return crud.get_lead_by_conversation(self.db, conversation_id)

    def get_hot_leads(self, threshold: int = 75) -> List[Lead]:
        return crud.get_high_value_leads(self.db, threshold)

    def sync_hubspot(self, lead_id: int, hubspot_id: str) -> Optional[Lead]:
        return crud.update_lead_hubspot(self.db, lead_id, hubspot_id)

    def mark_alert_sent(self, lead_id: int) -> Optional[Lead]:
        return crud.mark_alert_sent(self.db, lead_id)

    def get_stats(self) -> Dict[str, Any]:
        """Return lead pipeline statistics for reporting."""
        from sqlalchemy import func
        from models import LeadStatus

        total = self.db.query(Lead).count()
        hot = self.db.query(Lead).filter(Lead.status == LeadStatus.hot).count()
        warm = self.db.query(Lead).filter(Lead.status == LeadStatus.warm).count()
        cold = self.db.query(Lead).filter(Lead.status == LeadStatus.cold).count()
        avg_score = self.db.query(func.avg(Lead.score)).scalar() or 0
        synced = self.db.query(Lead).filter(Lead.hubspot_synced == True).count()  # noqa: E712

        return {
            "total_leads": total,
            "hot_leads": hot,
            "warm_leads": warm,
            "cold_leads": cold,
            "average_score": round(float(avg_score), 1),
            "hubspot_synced": synced,
        }


# ════════════════════════════════════════════════════════════════
#  LEAD SCORE REPOSITORY
# ════════════════════════════════════════════════════════════════

class LeadScoreRepository:
    """Handles all DB operations for LeadScore model."""

    def __init__(self, db: Session):
        self.db = db

    def save(self, conversation_id: str, score_data: Dict[str, Any]) -> Optional[LeadScore]:
        return crud.save_lead_score(self.db, conversation_id, score_data)

    def get_latest(self, conversation_id: str) -> Optional[LeadScore]:
        return crud.get_latest_score(self.db, conversation_id)

    def get_history(self, conversation_id: str) -> List[LeadScore]:
        return crud.get_score_history(self.db, conversation_id)

    def get_score_distribution(self) -> Dict[str, int]:
        """Return count of leads by score bucket (0-25, 26-50, 51-75, 76-100)."""
        buckets = {"0-25": 0, "26-50": 0, "51-75": 0, "76-100": 0}
        scores = self.db.query(LeadScore.overall_score).all()
        for (s,) in scores:
            if s <= 25:
                buckets["0-25"] += 1
            elif s <= 50:
                buckets["26-50"] += 1
            elif s <= 75:
                buckets["51-75"] += 1
            else:
                buckets["76-100"] += 1
        return buckets
