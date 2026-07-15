"""
schemas.py — Pydantic Request/Response Models
All API input/output validation schemas.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


# ── Enums ─────────────────────────────────────────────────────────────────────
class RecommendationEnum(str, Enum):
    route_to_sales = "route_to_sales"
    nurture = "nurture"
    marketing_only = "marketing_only"


class IntentLevelEnum(str, Enum):
    high = "High"
    medium = "Medium"
    low = "Low"


# ── Conversation ───────────────────────────────────────────────────────────────
class ConversationStartResponse(BaseModel):
    conversation_id: str
    opening_message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ── Message ────────────────────────────────────────────────────────────────────
class MessageRequest(BaseModel):
    user_message: str = Field(..., min_length=1, max_length=5000, description="User's message text")
    conversation_id: str = Field(..., description="UUID of the conversation")

    class Config:
        json_schema_extra = {
            "example": {
                "user_message": "Hi, we're growing fast and need a CRM solution",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class MessageResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    turn_count: Optional[int] = None


class MessageItem(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Scoring ────────────────────────────────────────────────────────────────────
class ScoreRequest(BaseModel):
    conversation_id: str = Field(..., description="UUID of the conversation to score")


class ScoreBreakdown(BaseModel):
    icp_fit: int = Field(..., ge=0, le=100, description="ICP fit score (30% weight)")
    intent_signals: int = Field(..., ge=0, le=100, description="Intent signals score (25% weight)")
    timeline: int = Field(..., ge=0, le=100, description="Timeline score (20% weight)")
    authority: int = Field(..., ge=0, le=100, description="Authority score (15% weight)")
    engagement: int = Field(..., ge=0, le=100, description="Engagement score (10% weight)")


class ScoreResponse(BaseModel):
    conversation_id: str
    overall_score: int = Field(..., ge=0, le=100)
    breakdown: ScoreBreakdown
    recommendation: RecommendationEnum
    reasoning: str
    # Elite BANT scoring fields (optional for backward compatibility)
    key_strengths: Optional[str] = Field(None, description="1-2 main positive factors making this lead compelling")
    key_gaps: Optional[str] = Field(None, description="1-2 main limiting factors or risks")
    next_step: Optional[str] = Field(None, description="Specific action for sales or marketing team")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "overall_score": 82,
                "breakdown": {
                    "icp_fit": 85,
                    "intent_signals": 80,
                    "timeline": 70,
                    "authority": 90,
                    "engagement": 75
                },
                "recommendation": "route_to_sales",
                "reasoning": "VP of Sales at 75-person B2B SaaS with acute pipeline visibility pain. Q3 budget allocated, decision-maker confirmed. Strong ICP alignment.",
                "key_strengths": "Executive-level authority, allocated Q3 budget, quantifiable pain ($200K/yr in lost deals)",
                "key_gaps": "CFO sign-off required for contracts >$50K; need to map procurement process",
                "next_step": "Route to AE immediately — schedule technical discovery with VP of Sales and loop in CFO for commercial conversation",
                "timestamp": "2026-07-04T17:00:00"
            }
        }


# ── Lead Qualification ──────────────────────────────────────────────────────────
class LeadQualifyRequest(BaseModel):
    conversation_id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    phone_number: Optional[str] = Field(None, description="Contact phone number (E.164 format preferred)")
    score: int = Field(..., ge=0, le=100)
    icp_fit: int = Field(..., ge=0, le=100)
    intent_level: Optional[IntentLevelEnum] = None
    timeline: Optional[str] = None
    use_case: Optional[str] = Field(None, description="Primary use case or pain point described by the lead")


class LeadQualifyResponse(BaseModel):
    status: str
    lead_id: Optional[int] = None
    hubspot_contact_id: Optional[str] = None
    score: int
    alert_sent: bool
    message: str


# ── Conversation History ─────────────────────────────────────────────────────
class ConversationHistoryResponse(BaseModel):
    conversation_id: str
    status: str
    messages: List[MessageItem]
    message_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Health ──────────────────────────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str
    database: str
    version: str = "1.1.0"
    environment: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
