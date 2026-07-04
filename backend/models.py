"""
models.py — SQLAlchemy ORM Models
Defines all database tables: Conversation, Message, Lead, LeadScore.
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Text, DateTime,
    ForeignKey, Enum as SAEnum, Float, Boolean
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
import enum


# ── Enums ────────────────────────────────────────────────────────────────────
class ConversationStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    converted = "converted"
    abandoned = "abandoned"


class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class LeadStatus(str, enum.Enum):
    hot = "hot"         # score >= 75
    warm = "warm"       # score 50-74
    cold = "cold"       # score < 50


class IntentLevel(str, enum.Enum):
    high = "High"
    medium = "Medium"
    low = "Low"


# ── Conversation ──────────────────────────────────────────────────────────────
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    status = Column(SAEnum(ConversationStatus), default=ConversationStatus.active, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    lead = relationship("Lead", back_populates="conversation", uselist=False, cascade="all, delete-orphan")
    lead_scores = relationship("LeadScore", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation {self.id} [{self.status}]>"


# ── Message ───────────────────────────────────────────────────────────────────
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(SAEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message {self.id} [{self.role}]>"


# ── Lead ──────────────────────────────────────────────────────────────────────
class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), unique=True, index=True)

    # Contact Info
    email = Column(String(255), index=True, nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    company = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)

    # Qualification Data
    score = Column(Integer, default=0, index=True)   # 0–100
    icp_fit = Column(Integer, default=0)              # 0–100
    intent_level = Column(SAEnum(IntentLevel), nullable=True)
    timeline = Column(String(100), nullable=True)
    status = Column(SAEnum(LeadStatus), nullable=True)

    # CRM
    hubspot_id = Column(String(100), nullable=True, index=True)
    hubspot_synced = Column(Boolean, default=False)
    alert_sent = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="lead")

    def __repr__(self):
        return f"<Lead {self.email} score={self.score}>"


# ── LeadScore ─────────────────────────────────────────────────────────────────
class LeadScore(Base):
    __tablename__ = "lead_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)

    # Score Breakdown (0–100 each)
    overall_score = Column(Integer, nullable=False)
    icp_fit = Column(Integer, nullable=False)          # 30% weight
    intent_signals = Column(Integer, nullable=False)   # 25% weight
    timeline = Column(Integer, nullable=False)         # 20% weight
    authority = Column(Integer, nullable=False)        # 15% weight
    engagement = Column(Integer, nullable=False)       # 10% weight

    # AI Reasoning
    reasoning = Column(Text, nullable=True)
    recommendation = Column(String(50), nullable=True)  # route_to_sales / nurture / marketing_only

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="lead_scores")

    def __repr__(self):
        return f"<LeadScore conv={self.conversation_id} score={self.overall_score}>"
