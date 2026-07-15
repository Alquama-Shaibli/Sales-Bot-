"""
routers/chat.py — Chat Endpoints
Handles conversation start, message exchange, and scoring triggers.
All Claude AI logic delegated to services/chat_service.py (Day 2).
"""
import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from schemas import (
    ConversationStartResponse,
    MessageRequest,
    MessageResponse,
    ScoreRequest,
    ScoreResponse,
    ConversationHistoryResponse,
    MessageItem,
)
from models import Conversation, Message, LeadScore, ConversationStatus, MessageRole

router = APIRouter()
logger = logging.getLogger(__name__)

# Opening message shown to every new prospect — elite consultative approach
OPENING_MESSAGE = (
    "👋 Hi there! I'm your EnterpriseLead AI specialist — I help B2B teams cut through "
    "qualification noise and focus on the right opportunities. "
    "To get started, what's the biggest friction point in your current sales or growth process right now?"
)


# ── POST /api/conversation/start ──────────────────────────────────────────────
@router.post(
    "/conversation/start",
    response_model=ConversationStartResponse,
    summary="Start a new lead qualification conversation",
)
async def start_conversation(db: Session = Depends(get_db)):
    """
    Creates a new conversation session and returns a conversation_id.
    The frontend stores this ID and sends it with every subsequent message.
    """
    try:
        # Create conversation record
        convo = Conversation(
            id=uuid.uuid4(),
            status=ConversationStatus.active,
        )
        db.add(convo)

        # Save opening message from assistant
        opening_msg = Message(
            conversation_id=convo.id,
            role=MessageRole.assistant,
            content=OPENING_MESSAGE,
        )
        db.add(opening_msg)
        db.commit()
        db.refresh(convo)

        logger.info(f"✅ New conversation started: {convo.id}")
        return ConversationStartResponse(
            conversation_id=str(convo.id),
            opening_message=OPENING_MESSAGE,
            timestamp=datetime.utcnow(),
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to start conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start conversation. Please try again.",
        )


# ── POST /api/message ──────────────────────────────────────────────────────────
@router.post(
    "/message",
    response_model=MessageResponse,
    summary="Send a user message and receive AI response",
)
async def send_message(request: MessageRequest, db: Session = Depends(get_db)):
    """
    Receives a user message, calls Claude API (via ChatService),
    stores both messages in DB, and returns the bot's response.
    Multi-turn context is maintained via conversation history from DB.
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

        if convo.status == ConversationStatus.abandoned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This conversation has ended.",
            )

        # Save user message
        user_msg = Message(
            conversation_id=convo.id,
            role=MessageRole.user,
            content=request.user_message.strip(),
        )
        db.add(user_msg)
        db.flush()

        # Get full conversation history for context
        history = (
            db.query(Message)
            .filter(Message.conversation_id == convo.id)
            .order_by(Message.created_at.asc())
            .all()
        )

        # ── Claude AI Call (injected in Day 2) ──────────────────────────────
        try:
            from services.chat_service import ChatService
            chat_service = ChatService()
            bot_response = await chat_service.get_response(
                user_message=request.user_message,
                conversation_history=history,
            )
        except ImportError:
            # Day 1 placeholder — real Claude integration added Day 2
            bot_response = (
                "Thanks for sharing that! Could you tell me a bit more about "
                "your company size and what industry you're in? That helps me "
                "understand if we're a good fit."
            )
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            bot_response = (
                "I appreciate your patience! I'm experiencing a brief issue. "
                "Could you repeat that?"
            )

        # Save bot response
        bot_msg = Message(
            conversation_id=convo.id,
            role=MessageRole.assistant,
            content=bot_response,
        )
        db.add(bot_msg)

        # Update conversation timestamp
        convo.updated_at = datetime.utcnow()
        db.commit()

        # Get message count for turn tracking
        turn_count = db.query(Message).filter(
            Message.conversation_id == convo.id,
            Message.role == MessageRole.user,
        ).count()

        logger.info(f"Message processed for conversation {convo.id} | Turn {turn_count}")
        return MessageResponse(
            response=bot_response,
            conversation_id=str(convo.id),
            timestamp=datetime.utcnow(),
            turn_count=turn_count,
        )

    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation_id format. Must be a valid UUID.",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Message endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message.",
        )


# ── POST /api/score ────────────────────────────────────────────────────────────
@router.post(
    "/score",
    response_model=ScoreResponse,
    summary="Score a completed conversation (0–100)",
)
async def score_conversation(request: ScoreRequest, db: Session = Depends(get_db)):
    """
    Evaluates the full conversation on 5 dimensions using Claude.
    Returns a 0–100 score with breakdown and recommendation.
    Scores are stored in DB for tracking.
    """
    try:
        convo = db.query(Conversation).filter(
            Conversation.id == uuid.UUID(request.conversation_id)
        ).first()

        if not convo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {request.conversation_id} not found.",
            )

        # Get all messages
        history = (
            db.query(Message)
            .filter(Message.conversation_id == convo.id)
            .order_by(Message.created_at.asc())
            .all()
        )

        if len(history) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conversation is too short to score. Have at least 2 exchanges.",
            )

        # ── Scoring Engine (injected in Day 2) ──────────────────────────────
        try:
            from services.scoring_service import ScoringService
            scoring_service = ScoringService()
            score_data = await scoring_service.score_conversation(history)
        except ImportError:
            # Day 1 placeholder
            score_data = {
                "icp_fit": 70,
                "intent_signals": 65,
                "timeline": 60,
                "authority": 55,
                "engagement": 80,
                "overall_score": 66,
                "reasoning": "Placeholder score — Claude scoring service will be active from Day 2.",
                "recommendation": "nurture",
            }

        # Determine recommendation
        overall = score_data["overall_score"]
        if overall >= 75:
            recommendation = "route_to_sales"
        elif overall >= 50:
            recommendation = "nurture"
        else:
            recommendation = "marketing_only"

        # Save score to DB
        lead_score = LeadScore(
            conversation_id=convo.id,
            overall_score=overall,
            icp_fit=score_data["icp_fit"],
            intent_signals=score_data["intent_signals"],
            timeline=score_data["timeline"],
            authority=score_data["authority"],
            engagement=score_data["engagement"],
            reasoning=score_data.get("reasoning", ""),
            recommendation=recommendation,
        )
        db.add(lead_score)

        # Mark conversation as completed
        convo.status = ConversationStatus.completed
        db.commit()

        logger.info(f"Scored conversation {convo.id}: {overall}/100 → {recommendation}")

        from schemas import ScoreBreakdown
        return ScoreResponse(
            conversation_id=request.conversation_id,
            overall_score=overall,
            breakdown=ScoreBreakdown(
                icp_fit=score_data["icp_fit"],
                intent_signals=score_data["intent_signals"],
                timeline=score_data["timeline"],
                authority=score_data["authority"],
                engagement=score_data["engagement"],
            ),
            recommendation=recommendation,
            reasoning=score_data.get("reasoning", ""),
            key_strengths=score_data.get("key_strengths"),
            key_gaps=score_data.get("key_gaps"),
            next_step=score_data.get("next_step"),
            timestamp=datetime.utcnow(),
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
        logger.error(f"Scoring error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to score conversation.",
        )


# ── GET /api/conversations/{conversation_id} ──────────────────────────────────
@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationHistoryResponse,
    summary="Get full conversation history",
)
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Returns the full message history for a conversation."""
    try:
        convo = db.query(Conversation).filter(
            Conversation.id == uuid.UUID(conversation_id)
        ).first()

        if not convo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found.",
            )

        messages = (
            db.query(Message)
            .filter(Message.conversation_id == convo.id)
            .order_by(Message.created_at.asc())
            .all()
        )

        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            status=convo.status.value,
            messages=[
                MessageItem(
                    id=m.id,
                    role=m.role.value,
                    content=m.content,
                    created_at=m.created_at,
                )
                for m in messages
            ],
            message_count=len(messages),
            created_at=convo.created_at,
        )

    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation_id format.",
        )
    except Exception as e:
        logger.error(f"Get conversation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation.",
        )
