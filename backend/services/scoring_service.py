"""
services/scoring_service.py — 5-Dimension Lead Scoring Engine
Uses Claude to evaluate conversations across 5 weighted dimensions.
Returns a 0-100 score with breakdown and explainable reasoning.
"""
import json
import logging
import re
from typing import List, Dict, Any

from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings
from models import Message

logger = logging.getLogger(__name__)

# ── Scoring Prompt ────────────────────────────────────────────────────────────
SCORING_PROMPT = """You are an expert B2B SaaS lead qualification analyst.
Analyze the following sales conversation and score the prospect on 5 dimensions.

SCORING DIMENSIONS AND WEIGHTS:

1. ICP_FIT (30% weight) — Does this company match our Ideal Customer Profile?
   - Target: 10–500 person B2B SaaS companies, tech-enabled, growing
   - Score HIGH (70-100): Clear fit with size, industry, growth stage
   - Score MEDIUM (40-69): Partial fit, some mismatches
   - Score LOW (0-39): Poor fit or unknown

2. INTENT_SIGNALS (25% weight) — How urgently do they need a solution?
   - Score HIGH (70-100): Active pain, specific problem, urgent need
   - Score MEDIUM (40-69): General interest, exploring options
   - Score LOW (0-39): Just browsing, no clear pain

3. TIMELINE (20% weight) — When will they buy?
   - Score HIGH (70-100): "This quarter", "This month", "ASAP"
   - Score MEDIUM (40-69): "Q3 or Q4", "H2 of this year"
   - Score LOW (0-39): "2027", "Just researching", "No timeline"

4. AUTHORITY (15% weight) — Can they make the buying decision?
   - Score HIGH (70-100): Decision-maker, confirmed budget access
   - Score MEDIUM (40-69): Influencer, needs approval from 1-2 people
   - Score LOW (0-39): End user, no buying power

5. ENGAGEMENT (10% weight) — Quality of their participation?
   - Score HIGH (70-100): Detailed answers, follow-up questions, genuine interest
   - Score MEDIUM (40-69): Short but relevant answers
   - Score LOW (0-39): Vague answers, seems distracted

CALCULATION:
overall_score = (icp_fit * 0.30) + (intent_signals * 0.25) + (timeline * 0.20) + (authority * 0.15) + (engagement * 0.10)

IMPORTANT: Return ONLY valid JSON in exactly this format, nothing else:
{
  "icp_fit": <0-100>,
  "intent_signals": <0-100>,
  "timeline": <0-100>,
  "authority": <0-100>,
  "engagement": <0-100>,
  "overall_score": <0-100>,
  "reasoning": "<2-3 sentences explaining the overall score and key factors>",
  "key_signals": ["<signal 1>", "<signal 2>", "<signal 3>"]
}
"""


class ScoringService:
    """Scores lead conversations using Claude across 5 weighted dimensions."""

    # Score weights (must sum to 1.0)
    WEIGHTS = {
        "icp_fit": 0.30,
        "intent_signals": 0.25,
        "timeline": 0.20,
        "authority": 0.15,
        "engagement": 0.10,
    }

    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model
        logger.info("ScoringService initialized")

    def _format_conversation_for_scoring(self, history: List[Message]) -> str:
        """Format conversation history as readable text for scoring."""
        lines = []
        for msg in history:
            role = msg.role.value if hasattr(msg.role, "value") else str(msg.role)
            if role == "user":
                lines.append(f"PROSPECT: {msg.content}")
            elif role == "assistant":
                lines.append(f"SALES BOT: {msg.content}")
        return "\n\n".join(lines)

    def _calculate_weighted_score(self, scores: Dict[str, int]) -> int:
        """
        Calculate the weighted overall score.
        Overrides Claude's calculation to ensure formula accuracy.
        """
        total = sum(
            scores.get(dim, 0) * weight
            for dim, weight in self.WEIGHTS.items()
        )
        return round(total)

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from Claude's response.
        Handles cases where Claude adds extra text around the JSON.
        """
        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting JSON block
        json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Fallback: return default scores
        logger.warning("Could not parse Claude scoring response — using defaults")
        return self._default_scores()

    def _default_scores(self) -> Dict[str, Any]:
        """Safe fallback scores when Claude response can't be parsed."""
        return {
            "icp_fit": 50,
            "intent_signals": 50,
            "timeline": 50,
            "authority": 50,
            "engagement": 50,
            "overall_score": 50,
            "reasoning": "Score could not be determined from the conversation. Please review manually.",
            "key_signals": ["Insufficient data"],
        }

    def _validate_scores(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all scores are integers in range 0-100."""
        dimensions = ["icp_fit", "intent_signals", "timeline", "authority", "engagement"]
        for dim in dimensions:
            val = data.get(dim, 50)
            data[dim] = max(0, min(100, int(val)))

        # Recalculate overall to ensure formula accuracy
        data["overall_score"] = self._calculate_weighted_score(data)

        if not isinstance(data.get("reasoning"), str):
            data["reasoning"] = "Unable to generate reasoning."

        if not isinstance(data.get("key_signals"), list):
            data["key_signals"] = []

        return data

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=False,
    )
    async def score_conversation(self, history: List[Message]) -> Dict[str, Any]:
        """
        Main scoring function. Evaluates a full conversation.

        Args:
            history: List of Message objects from the conversation

        Returns:
            Dict with: icp_fit, intent_signals, timeline, authority,
                       engagement, overall_score, reasoning, key_signals
        """
        if not history:
            logger.warning("Empty conversation history — returning default scores")
            return self._default_scores()

        conversation_text = self._format_conversation_for_scoring(history)

        scoring_messages = [
            {
                "role": "user",
                "content": (
                    f"Please score this sales conversation:\n\n"
                    f"---CONVERSATION START---\n"
                    f"{conversation_text}\n"
                    f"---CONVERSATION END---\n\n"
                    f"Return JSON only, no other text."
                ),
            }
        ]

        try:
            logger.info(f"Scoring conversation ({len(history)} messages)...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=600,
                system=SCORING_PROMPT,
                messages=scoring_messages,
            )

            raw_text = response.content[0].text.strip()
            logger.debug(f"Claude scoring raw response: {raw_text[:200]}")

            # Parse and validate
            score_data = self._extract_json(raw_text)
            score_data = self._validate_scores(score_data)

            logger.info(
                f"✅ Scoring complete | "
                f"Overall: {score_data['overall_score']} | "
                f"ICP: {score_data['icp_fit']} | "
                f"Intent: {score_data['intent_signals']} | "
                f"Timeline: {score_data['timeline']} | "
                f"Authority: {score_data['authority']} | "
                f"Engagement: {score_data['engagement']}"
            )
            return score_data

        except Exception as e:
            logger.error(f"Scoring failed after retries: {e}")
            return self._default_scores()

    def get_recommendation(self, overall_score: int) -> str:
        """Returns routing recommendation based on score."""
        if overall_score >= 75:
            return "route_to_sales"
        elif overall_score >= 50:
            return "nurture"
        else:
            return "marketing_only"

    def get_score_label(self, overall_score: int) -> str:
        """Returns human-readable label."""
        if overall_score >= 75:
            return "🔴 Hot Lead"
        elif overall_score >= 50:
            return "🟡 Warm Lead"
        else:
            return "🔵 Cold Lead"
