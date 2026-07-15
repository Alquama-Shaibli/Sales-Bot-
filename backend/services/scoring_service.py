"""
services/scoring_service.py — Elite 5-Dimension Lead Scoring Engine
Uses Claude to evaluate conversations across 5 weighted BANT-extended dimensions.
Produces business-driven, explainable scoring with specific conversation references.
Returns 0-100 score with detailed breakdown, reasoning, and strategic recommendations.
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

# ── Elite Scoring Prompt ────────────────────────────────────────────────────────
SCORING_PROMPT = """You are an expert B2B SaaS revenue operations analyst with 15+ years of experience evaluating enterprise software deals.

Your role: Analyze the conversation below and produce a BUSINESS-DRIVEN, DATA-INFORMED assessment of this lead's quality and readiness for sales.

KEY CONTEXT:
- This is for a B2B SaaS company with $50K–$500K typical ACV
- Average sales cycle: 60–90 days
- Sales rep bandwidth: 8–12 active opportunities per rep
- Cost of misaligned lead routing: Significant (SDR time waste, forecast disruption)
- Scoring serves as gating: Scores 75+ route to sales immediately, 50–74 nurture, <50 marketing-only

YOUR SCORING FRAMEWORK:

1. ICP FIT (30% weight) — Does this prospect match our Ideal Customer Profile?

SCORING RUBRIC:
90–100: Perfect fit on all dimensions
  Example: 80-person B2B SaaS company in target vertical, 40% YoY growth
75–89: Strong fit on most dimensions, minor gaps
  Example: 150-person adjacent SaaS company, 25% growth, slightly larger than ideal
60–74: Good fit on core dimensions, some misalignment
  Example: 300-person company in our industry, but different business model
40–59: Partial fit, notable gaps but not disqualifying
  Example: 500+ person enterprise, large but could be good deal size
0–39: Poor fit, significant misalignment with ICP
  Example: 5-person startup or 5000-person consumer company

EVIDENCE TO LOOK FOR:
- Company size indicators: "80 person team", "hit $50M ARR", "scaled to 10 countries"
- Growth signals: "Growing 50% YoY", "Just closed Series B", "Expanding rapidly"
- Industry relevance: "We're a SaaS company", "B2B space", "Enterprise software"
- Technical maturity: References to systems, integrations, APIs, automation needs

2. INTENT SIGNALS (25% weight) — How urgent and real is their need?

SCORING RUBRIC:
90–100: Clear acute pain, executive awareness, budget allocated
  Example: "We lose $50K/month to manual processes. CFO wants it solved Q3."
75–89: Significant problem, acknowledged pain, budget likely
  Example: "This is hurting our sales team. We've gotten budget approval."
60–74: Identified problem, exploring solutions, budget conversation happening
  Example: "We know we need a better way. We're looking at options."
40–59: Awareness of problem but not urgent, budget unclear
  Example: "We've thought about this. Not sure when we'll act."
0–39: Just browsing, no acute problem, exploratory only
  Example: "Just wanted to learn what's out there."

EVIDENCE TO LOOK FOR:
- Urgency language: "ASAP", "urgent", "critical", "problem", "pain", "this quarter"
- Impact language: "Costing us money", "Affecting revenue", "Hurting productivity", "Blocking growth"
- Budget language: "Budget approved", "Allocated", "Can spend", "Getting funds"
- Active buying signals: "Evaluating", "Comparing", "Piloting", "Demo", "Implementation"
- Negative signals: "Just exploring", "Maybe later", "Not sure", "Still deciding"

3. TIMELINE (20% weight) — When are they likely to make a buying decision?

SCORING RUBRIC:
90–100: This quarter or next (Immediate need, buying process already started)
  Example: "Need this by Q3. Budget is in place. Already started evaluation."
75–89: Within 6 months (Clear timeline, budget cycle known, active evaluation)
  Example: "Decision by end of Q3. Budget comes in July."
60–74: Within 12 months (Planning ahead, budget cycle understood, not desperate)
  Example: "Implementing something in 2026. Building the business case now."
40–59: Sometime next year or later (Longer timeframe, but interested)
  Example: "Maybe next year. We're not in a rush."
0–39: No clear timeline, just researching
  Example: "We're just exploring options for now."

EVIDENCE TO LOOK FOR:
- Timeline language: "This quarter", "Q3", "This month", "Before year-end"
- Urgency triggers: "Compliance deadline", "Integration requirement", "Growth hiring"
- Budget cycles: "After board meeting", "Next fiscal year", "When annual budget resets"
- Implementation readiness: "We have IT support", "Project manager assigned"

4. AUTHORITY (15% weight) — Can this person make or influence the buying decision?

SCORING RUBRIC:
90–100: Clear economic buyer or executive sponsor
  Example: "I'm the VP of Sales. I control the tools budget."
75–89: Department head or budget holder with real authority
  Example: "I'm the director. I have authority to approve this spend."
60–74: Manager with influence over decisions
  Example: "I'll make the recommendation. My manager will approve."
40–59: Key stakeholder but not final decision-maker
  Example: "I use the tool daily. I have input, but the VP decides."
0–39: End user or analyst with limited influence
  Example: "I'm the one who'll use it, but someone above me decides."

EVIDENCE TO LOOK FOR:
- Authority language: "I decide", "I approve", "I control budget", "Final decision maker"
- Committee language: "We'll need approval from", "Stakeholders include", "Multiple people"
- Recommendation language: "I'll recommend", "I have influence", "They trust my opinion"
- Limited authority language: "Just evaluating", "Not my decision", "Someone else approves"

5. ENGAGEMENT (10% weight) — How interested and communicative are they?

SCORING RUBRIC:
90–100: Highly engaged — detailed responses, asks follow-up questions, enthusiastic
75–89: Well engaged — provides context, some examples, responsive
60–74: Moderately engaged — answers questions, some detail
40–59: Minimally engaged — brief answers, vague responses
0–39: Disengaged — one-word answers, not asking questions

EVIDENCE TO LOOK FOR:
- Engagement: Message length, specificity, examples given
- Tone: Enthusiasm vs skepticism vs neutrality
- Interest: References earlier points, asks clarifying questions
- Participation: Asks their own questions vs only answering yours

OVERALL SCORE CALCULATION:
overall_score = (icp_fit × 0.30) + (intent_signals × 0.25) + (timeline × 0.20) + (authority × 0.15) + (engagement × 0.10)

Interpretation:
75–100: "route_to_sales" → Sales-ready lead, hand off immediately
50–74: "nurture" → Add to nurture sequence, check back in 30–60 days
0–49: "marketing_only" → Focus on awareness and education, revisit when signals improve

REASONING QUALITY IS CRITICAL:
Your reasoning should:
- Reference SPECIFIC quotes or details from the conversation (not generic)
- Show you understood the nuances (competing priorities, organizational dynamics)
- Connect to business outcomes (how this affects their revenue/operations)
- Acknowledge trade-offs (e.g., "Perfect ICP but long timeline means...")
- Use professional B2B SaaS language (MQL, SQL, decision committee, stakeholder mapping)

EXAMPLE STRONG REASONING:
"Strong ICP fit (VP of Sales at 75-person SaaS) with acute pain (losing 15% of deals to manual process).
Timeline is favorable (Q3 budget allocated). However, decision requires CFO approval — need to identify
and engage economic buyer. Recommendation: Route to sales with focus on champion development and CFO
engagement strategy before technical deep-dive."

EXAMPLE WEAK REASONING:
"They seem interested. Score is 78 because they're a good fit. Should route to sales."

CRITICAL INSTRUCTION:
Return ONLY valid JSON. No other text. No markdown code fences. Just the JSON object.

{
  "icp_fit": <0-100 integer based on rubric>,
  "intent_signals": <0-100 integer based on urgency and pain>,
  "timeline": <0-100 integer based on buying timeline>,
  "authority": <0-100 integer based on decision power>,
  "engagement": <0-100 integer based on responsiveness>,
  "overall_score": <0-100 integer calculated from above>,
  "reasoning": "<2-3 sentences with SPECIFIC details from conversation, not generic>",
  "key_strengths": "<1-2 main positive factors that make this lead compelling>",
  "key_gaps": "<1-2 main limiting factors or risks to be aware of>",
  "next_step": "<specific action the sales or marketing team should take based on score and situation>"
}"""


class ScoringService:
    """Scores lead conversations using Claude across 5 weighted BANT-extended dimensions."""

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
        logger.info("ScoringService initialized (Elite BANT mode)")

    def _format_conversation_for_scoring(self, history: List[Message]) -> str:
        """Format conversation history as readable text for Claude scoring analysis."""
        lines = []
        for msg in history:
            role = msg.role.value if hasattr(msg.role, "value") else str(msg.role)
            if role == "user":
                lines.append(f"PROSPECT: {msg.content}")
            elif role == "assistant":
                lines.append(f"SALES AGENT: {msg.content}")
        return "\n\n".join(lines)

    def _calculate_weighted_score(self, scores: Dict[str, int]) -> int:
        """
        Calculate the weighted overall score using the exact formula.
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
        Handles cases where Claude adds extra text or markdown fences.
        """
        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Strip markdown code fences if present
        clean = re.sub(r'```(?:json)?', '', text).strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            pass

        # Try extracting largest JSON block
        json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

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
            "key_strengths": "Engaged in qualification conversation",
            "key_gaps": "Insufficient data for detailed BANT assessment",
            "next_step": "Continue qualification to gather company size, timeline, and decision-maker information",
        }

    def _validate_scores(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all scores are integers in range 0–100 and all required fields are present."""
        dimensions = ["icp_fit", "intent_signals", "timeline", "authority", "engagement"]
        for dim in dimensions:
            val = data.get(dim, 50)
            data[dim] = max(0, min(100, int(val)))

        # Recalculate overall to ensure formula accuracy
        data["overall_score"] = self._calculate_weighted_score(data)

        if not isinstance(data.get("reasoning"), str) or not data.get("reasoning"):
            data["reasoning"] = "Unable to generate reasoning."

        # Ensure new elite fields are present (backfill if missing from older responses)
        if not isinstance(data.get("key_strengths"), str) or not data.get("key_strengths"):
            data["key_strengths"] = "Prospect engaged in qualification process"

        if not isinstance(data.get("key_gaps"), str) or not data.get("key_gaps"):
            data["key_gaps"] = "Additional qualification needed for complete BANT assessment"

        if not isinstance(data.get("next_step"), str) or not data.get("next_step"):
            overall = data.get("overall_score", 50)
            if overall >= 75:
                data["next_step"] = "Route to sales immediately — assign to AE and schedule discovery call"
            elif overall >= 50:
                data["next_step"] = "Add to nurture sequence — follow up in 30 days with educational content"
            else:
                data["next_step"] = "Add to marketing-only list — focus on awareness and problem education"

        return data

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=False,
    )
    async def score_conversation(self, history: List[Message]) -> Dict[str, Any]:
        """
        Main scoring function. Evaluates a full conversation using elite BANT framework.

        Args:
            history: List of Message objects from the conversation

        Returns:
            Dict with: icp_fit, intent_signals, timeline, authority,
                       engagement, overall_score, reasoning, key_strengths,
                       key_gaps, next_step
        """
        if not history:
            logger.warning("Empty conversation history — returning default scores")
            return self._default_scores()

        conversation_text = self._format_conversation_for_scoring(history)

        scoring_messages = [
            {
                "role": "user",
                "content": (
                    f"Please score this sales conversation using the BANT framework:\n\n"
                    f"---CONVERSATION START---\n"
                    f"{conversation_text}\n"
                    f"---CONVERSATION END---\n\n"
                    f"Return valid JSON only, no other text. Include key_strengths, key_gaps, and next_step fields."
                ),
            }
        ]

        try:
            logger.info(f"Scoring conversation ({len(history)} messages) with elite BANT framework...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                system=SCORING_PROMPT,
                messages=scoring_messages,
            )

            raw_text = response.content[0].text.strip()
            logger.debug(f"Claude scoring raw response: {raw_text[:300]}")

            # Parse and validate
            score_data = self._extract_json(raw_text)
            score_data = self._validate_scores(score_data)

            logger.info(
                f"✅ Elite scoring complete | "
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
        """Returns routing recommendation based on overall score."""
        if overall_score >= 75:
            return "route_to_sales"
        elif overall_score >= 50:
            return "nurture"
        else:
            return "marketing_only"

    def get_score_label(self, overall_score: int) -> str:
        """Returns human-readable lead temperature label."""
        if overall_score >= 75:
            return "🔴 Hot Lead"
        elif overall_score >= 50:
            return "🟡 Warm Lead"
        else:
            return "🔵 Cold Lead"
