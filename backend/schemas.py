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
                "reasoning": "Series B SaaS company, 50-person team, clear pain point, VP-level decision maker, Q3 timeline.",
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
    score: int = Field(..., ge=0, le=100)
    icp_fit: int = Field(..., ge=0, le=100)
    intent_level: Optional[IntentLevelEnum] = None
    timeline: Optional[str] = None


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
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
