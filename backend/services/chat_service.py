"""
services/chat_service.py — Claude API Integration
Handles multi-turn conversation with Claude claude-3-5-sonnet-20241022.
Maintains conversation context and generates natural qualifying responses.
"""
import logging
import re
from typing import List
from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings
from models import Message

logger = logging.getLogger(__name__)

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert B2B SaaS sales qualification specialist named Alex.
Your job is to qualify leads through natural, conversational dialogue — NOT a robotic questionnaire.

YOUR GOAL: Discover in 4-6 messages whether this prospect is a good fit.

QUALIFICATION DIMENSIONS (gather naturally):
1. INTENT  — What specific problem are they solving? How urgent is it?
2. COMPANY — Company size? Industry? Growth stage?
3. USE CASE — How would they use the solution? What does success look like?
4. TIMELINE — When do they want to implement? Is this a Q3 priority?
5. AUTHORITY — Are they the decision-maker? Who else is involved?

CONVERSATION RULES:
✅ Ask ONE question per message — never more
✅ Acknowledge their answer before asking the next question
✅ Use casual, friendly language (not corporate speak)
✅ Reference what they've already said (show you're listening)
✅ Use occasional emojis where natural 😊
✅ After 4-5 exchanges, summarize what you've learned

❌ NEVER ask about budget directly — it kills 60% of conversations
❌ NEVER sound like a bot — vary your responses
❌ NEVER repeat a question you've already asked
❌ NEVER ask 2 questions at once

EXAMPLE GOOD RESPONSE:
"Spreadsheets definitely don't scale past 20 people 😅 How many salespeople are you currently managing?"

EXAMPLE BAD RESPONSE:
"Please fill in the following: 1. Company size? 2. Industry? 3. Budget?"

After 4-6 exchanges, if you have enough info, say:
"Great — I think I have a solid picture of your situation. Would you like me to assess how well we'd be a fit?"
"""


class ChatService:
    """Manages multi-turn conversations with Claude API."""

    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model
        self.max_tokens = settings.max_tokens
        logger.info(f"ChatService initialized with model: {self.model}")

    def _format_history(self, history: List[Message]) -> List[dict]:
        """
        Convert SQLAlchemy Message objects to Claude API message format.
        Skips system messages; only includes user/assistant turns.
        """
        formatted = []
        for msg in history:
            role = msg.role.value if hasattr(msg.role, 'value') else str(msg.role)
            if role in ("user", "assistant"):
                formatted.append({
                    "role": role,
                    "content": msg.content,
                })
        return formatted

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def get_response(
        self,
        user_message: str,
        conversation_history: List[Message],
    ) -> str:
        """
        Send user message to Claude with full conversation context.
        Returns Claude's response text.

        Args:
            user_message: Latest message from the user
            conversation_history: All previous messages (from DB)

        Returns:
            str: Claude's response
        """
        try:
            # Format history (excludes the latest user message — it's already in history)
            messages = self._format_history(conversation_history)

            # Ensure conversation ends with user message
            if not messages or messages[-1]["role"] != "user":
                messages.append({"role": "user", "content": user_message})

            logger.debug(f"Sending {len(messages)} messages to Claude")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=SYSTEM_PROMPT,
                messages=messages,
            )

            bot_text = response.content[0].text.strip()
            logger.info(f"Claude response received ({len(bot_text)} chars)")
            return bot_text

        except Exception as e:
            logger.error(f"Claude API error: {type(e).__name__}: {e}")
            raise

    async def get_conversation_summary(self, history: List[Message]) -> str:
        """
        Ask Claude to summarize what it's learned about the prospect.
        Used as context for the scoring service.
        """
        messages = self._format_history(history)

        if not messages:
            return "No conversation history available."

        summary_prompt = (
            "Based on this conversation, provide a brief 3-4 sentence summary of what you've "
            "learned about this prospect: their problem, company, timeline, and role. "
            "Be factual and concise."
        )

        messages.append({"role": "user", "content": summary_prompt})

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                system="You are analyzing a sales conversation to extract key lead qualification data.",
                messages=messages,
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return "Summary unavailable."
