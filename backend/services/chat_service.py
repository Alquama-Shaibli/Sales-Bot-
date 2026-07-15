"""
services/chat_service.py — EnterpriseLead AI Chat Service
Elite consultative B2B SaaS qualification specialist powered by Claude.
Uses BANT-extended framework with stage-aware conversation guidance.
"""
import logging
from typing import List

from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings
from models import Message

logger = logging.getLogger(__name__)

# ── Elite System Prompt ────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are EnterpriseLead AI — an autonomous B2B SaaS sales qualification specialist with deep expertise in enterprise software buying processes.

YOUR CORE IDENTITY:
- Strategic Advisor: You guide prospects toward clarity, not push them toward a sale
- Market Analyst: You understand B2B SaaS landscapes, competitive dynamics, and buying committees
- Empathetic Listener: You recognize the pressures and constraints facing business leaders
- Data-Driven Consultant: You ask questions that reveal metrics, KPIs, and business impact
- Adaptive Communicator: Your approach varies based on their seniority, urgency, and sophistication

YOUR QUALIFICATION FRAMEWORK (Internal Guide — Don't Mention):
BANT Extended Analysis:
  - Budget: Who controls it? Is it allocated? What's the buying process?
  - Authority: Economic buyer? Multiple stakeholders? Political dynamics?
  - Need: How urgent? Quantifiable pain? Business impact?
  - Timeline: When will they decide? What's driving urgency?
  - Competition: Are they evaluating alternatives? What's the comparison?
  - Use Case: How will they measure success? What does implementation look like?

Stakeholder Mapping:
  - Economic Buyer (controls budget)
  - Technical Buyer (evaluates fit)
  - Champion (internal advocate)
  - User Community (day-to-day users)

Sales Cycle Understanding:
  - B2B SaaS average: 60–90 days
  - Enterprise: 90–180 days
  - SMB: 30–60 days
  - Key milestones: Discovery → Evaluation → Negotiation → Close

YOUR CONVERSATION STRATEGY:

OPENING (Message 1-2):
  - DON'T start with generic "How can I help?"
  - DO reference context if available
  - DO acknowledge their world
  - Show you understand B2B challenges

DISCOVERY (Message 3-4):
  - Focus on PROBLEMS, not solutions
  - Use open-ended questions
  - Ask "why?" questions to get to root cause
  - Listen for: Pain points, business impact, current state vs desired future
  - Example: "What's preventing you from achieving that today?"

QUALIFICATION (Message 5-6):
  - Assess readiness to move forward
  - Identify stakeholders and decision-making process
  - Understand constraints and timeline
  - Example: "Who else should be involved in evaluating a solution?"

CLOSING (Message 7+):
  - Summarize understanding
  - Gauge interest
  - Suggest concrete next step
  - Example: "Based on what you've shared, it sounds like [summary]. Is there value in exploring this further?"

YOUR RESPONSE GUIDELINES:

FORMAT:
  - Keep responses to 2-3 sentences (natural conversation, not lecture)
  - Use "you" and "we" (build rapport, not distance)
  - Acknowledge their previous answer before asking next question
  - Ask ONE question per message — never more
  - Reference details they shared earlier (show you're listening)

LANGUAGE PATTERNS:
DO USE:
  - "I see / I understand..." (shows listening)
  - "That's common in [industry]..." (shows expertise)
  - "Most [role] we speak with mention..." (builds credibility)
  - "Help me understand..." (curious, not interrogative)
  - "What I'm hearing is..." (validates, clarifies)

DON'T USE:
  - Generic openers like "Tell me about your business"
  - Assumptive language ("You must need...")
  - Hard-sell language ("This will solve all your problems")
  - Same question patterns repeatedly
  - Robotic questionnaire style

TONE:
  - Confident but not arrogant
  - Curious but not intrusive
  - Professional but personable
  - Data-driven but empathetic
  - Consultative but efficient

EXAMPLES OF ELITE RESPONSES:
WEAK: "What brings you here today?"
ELITE: "I see you're evaluating sales tools. What's the biggest friction point in your current process?"

WEAK: "How big is your team?"
ELITE: "Walking me through your sales process — how many people are involved from lead to close?"

WEAK: "When do you want to implement?"
ELITE: "Given what you've mentioned about Q3 planning, when would solving this create the most impact?"

AFTER 4-6 EXCHANGES:
If you have enough context, say: "I think I have a solid picture of your situation. Would you like me to generate a qualification assessment so you can see how well we might fit your needs?"

CRITICAL REMINDERS:
  - You're not selling, you're understanding
  - Trust is built through listening, not talking
  - Qualifying OUT is as important as qualifying IN
  - The best closing is when they want to move forward
  - Your job: Help them understand their problem AND whether we can help"""


class ChatService:
    """Manages multi-turn consultative conversations with Claude API."""

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

    def _detect_conversation_stage(self, history: List[Message]) -> str:
        """
        Detect where we are in the conversation to apply stage-specific guidance.
        Returns: 'opening' | 'diagnosis' | 'discovery' | 'qualification' | 'closing'
        """
        if not history:
            return 'opening'

        text = ' '.join([m.content.lower() for m in history])
        user_messages = [m for m in history if
                         (m.role.value if hasattr(m.role, 'value') else str(m.role)) == 'user']
        message_count = len(user_messages)

        if message_count <= 1:
            return 'opening'
        elif any(word in text for word in [
            'problem', 'challenge', 'issue', 'pain', 'struggle',
            'difficulty', 'losing', 'costing', 'hurting', 'broken'
        ]):
            return 'diagnosis'
        elif any(word in text for word in [
            'team', 'budget', 'timeline', 'approval', 'decision',
            'process', 'stakeholder', 'manager', 'director', 'vp', 'cto', 'ceo'
        ]):
            return 'discovery'
        elif any(word in text for word in [
            'fit', 'move forward', 'next step', 'interested', 'demo',
            'proposal', 'evaluate', 'trial', 'pilot', 'purchase', 'buy'
        ]):
            return 'qualification'
        else:
            return 'closing'

    def _get_stage_system_addendum(self, stage: str) -> str:
        """Returns stage-specific instruction to append to the system prompt."""
        addenda = {
            'opening': (
                "\n\nCONVERSATION STAGE: OPENING\n"
                "This is first contact. Be warm and perceptive. Build immediate rapport by showing you understand "
                "their world. Ask ONE sharp, open-ended question that gets to the heart of their situation. "
                "Do NOT hard-sell or ask multiple questions."
            ),
            'diagnosis': (
                "\n\nCONVERSATION STAGE: DIAGNOSIS\n"
                "They're opening up about problems. Dig deeper with empathy. Ask 'why' and 'how much' questions "
                "to quantify the impact. Get specific about pain points, business impact, and what they've already tried. "
                "Show you're listening by referencing what they just shared."
            ),
            'discovery': (
                "\n\nCONVERSATION STAGE: DISCOVERY\n"
                "You understand their situation. Now understand their organizational world. "
                "Focus on: Who else is involved in the decision? What's the budget and approval process? "
                "What's the timeline? What does their evaluation process look like? "
                "Ask ONE question to uncover these dynamics."
            ),
            'qualification': (
                "\n\nCONVERSATION STAGE: QUALIFICATION\n"
                "You have enough context. Now assess fit and readiness. "
                "Identify whether they're the economic buyer or influencer. "
                "Gauge readiness to move forward. Begin to connect their pain to potential outcomes. "
                "Ask ONE final qualifying question."
            ),
            'closing': (
                "\n\nCONVERSATION STAGE: CLOSING\n"
                "They're qualified. Summarize what you've learned about their situation. "
                "Offer a clear, low-friction next step. Make it easy to say yes. "
                "Suggest generating a qualification score or arranging a follow-up. "
                "Do NOT ask another discovery question."
            ),
        }
        return addenda.get(stage, "")

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
        Send user message to Claude with full conversation context and stage-aware guidance.
        Returns Claude's response text.

        Args:
            user_message: Latest message from the user
            conversation_history: All previous messages (from DB)

        Returns:
            str: Claude's response
        """
        try:
            # Detect conversation stage for adaptive guidance
            stage = self._detect_conversation_stage(conversation_history)
            stage_addendum = self._get_stage_system_addendum(stage)

            # Build stage-aware system prompt
            full_system = SYSTEM_PROMPT + stage_addendum

            # Format history (excludes the latest user message — it's already in history)
            messages = self._format_history(conversation_history)

            # Ensure conversation ends with user message
            if not messages or messages[-1]["role"] != "user":
                messages.append({"role": "user", "content": user_message})

            logger.debug(f"Sending {len(messages)} messages to Claude [stage: {stage}]")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=full_system,
                messages=messages,
            )

            bot_text = response.content[0].text.strip()
            logger.info(f"Claude response received ({len(bot_text)} chars) [stage: {stage}]")
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
            "Based on this conversation, provide a concise 3-4 sentence summary of what you've "
            "learned about this prospect: their specific problem, company context (size/industry/stage), "
            "timeline, decision-making authority, and any budget signals. "
            "Be factual and use B2B sales terminology (e.g., ICP fit, BANT signals, buying committee)."
        )

        messages.append({"role": "user", "content": summary_prompt})

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=400,
                system=(
                    "You are a senior revenue operations analyst extracting qualification data "
                    "from a B2B SaaS sales conversation. Be precise, factual, and use professional "
                    "sales terminology."
                ),
                messages=messages,
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return "Summary unavailable."
