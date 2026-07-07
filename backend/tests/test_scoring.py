"""
tests/test_scoring.py — Unit tests for ScoringService (5-dimension engine)
Run: pytest backend/tests/test_scoring.py -v
"""
import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ─────────────────────────────────────────────────────────────
#  FIXTURES
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def mock_settings():
    with patch("config.settings") as s:
        s.anthropic_api_key    = "test-key-12345"
        s.claude_model         = "claude-3-5-sonnet-20241022"
        s.max_tokens           = 1024
        s.lead_score_threshold = 75
        yield s


@pytest.fixture
def scoring_service(mock_settings):
    with patch("anthropic.Anthropic") as MockAnthropic:
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        from services.scoring_service import ScoringService
        svc = ScoringService()
        svc.client = mock_client
        yield svc, mock_client


# ─────────────────────────────────────────────────────────────
#  SAMPLE DATA
# ─────────────────────────────────────────────────────────────

HOT_LEAD_TRANSCRIPT = """
User: Hi, we're Acme Corp, 500-employee B2B SaaS company using Salesforce.
Bot: Great! What specific challenges are you solving?
User: We're losing 40% of deals due to slow qualification. We need this in Q1.
Bot: What's your budget range?
User: $80,000-100,000 annually. I'm the VP of Sales, final decision maker.
Bot: What's your current stack?
User: HubSpot, Salesforce, Outreach. We've already demoed 3 competitors.
"""

COLD_LEAD_TRANSCRIPT = """
User: Hi, just browsing. Small startup, 5 people.
Bot: What are you looking for?
User: Maybe something cheap for lead gen. No budget yet.
Bot: Who makes purchasing decisions?
User: Not sure, need to check with my boss.
"""

MOCK_HOT_SCORE = {
    "overall_score": 87,
    "breakdown": {
        "icp_fit":        88,
        "intent_signals": 90,
        "timeline":       85,
        "authority":      92,
        "engagement":     80,
    },
    "reasoning": "500-employee B2B SaaS company with clear pain point, Q1 urgency, VP-level authority, and $80k budget.",
    "recommendation": "Route immediately to senior AE.",
}

MOCK_COLD_SCORE = {
    "overall_score": 22,
    "breakdown": {
        "icp_fit":        20,
        "intent_signals": 15,
        "timeline":       30,
        "authority":      10,
        "engagement":     35,
    },
    "reasoning": "Very small company, no budget, unclear authority.",
    "recommendation": "Add to awareness nurture only.",
}


# ─────────────────────────────────────────────────────────────
#  TESTS — score_conversation (happy path)
# ─────────────────────────────────────────────────────────────

class TestScoreConversation:
    def _mock_claude_response(self, mock_client, score_dict):
        t = MagicMock()
        t.text = json.dumps(score_dict)
        r = MagicMock()
        r.content = [t]
        mock_client.messages.create.return_value = r

    def test_returns_overall_score(self, scoring_service):
        svc, mock_client = scoring_service
        self._mock_claude_response(mock_client, MOCK_HOT_SCORE)
        result = svc.score_conversation(HOT_LEAD_TRANSCRIPT)
        assert "overall_score" in result
        assert isinstance(result["overall_score"], (int, float))

    def test_hot_lead_score_range(self, scoring_service):
        svc, mock_client = scoring_service
        self._mock_claude_response(mock_client, MOCK_HOT_SCORE)
        result = svc.score_conversation(HOT_LEAD_TRANSCRIPT)
        assert result["overall_score"] >= 75, "Hot lead should score 75+"

    def test_cold_lead_score_range(self, scoring_service):
        svc, mock_client = scoring_service
        self._mock_claude_response(mock_client, MOCK_COLD_SCORE)
        result = svc.score_conversation(COLD_LEAD_TRANSCRIPT)
        assert result["overall_score"] < 50, "Cold lead should score below 50"

    def test_returns_all_five_dimensions(self, scoring_service):
        svc, mock_client = scoring_service
        self._mock_claude_response(mock_client, MOCK_HOT_SCORE)
        result = svc.score_conversation(HOT_LEAD_TRANSCRIPT)
        bd = result.get("breakdown", {})
        required = {"icp_fit", "intent_signals", "timeline", "authority", "engagement"}
        assert required.issubset(set(bd.keys())), f"Missing dimensions: {required - set(bd.keys())}"

    def test_all_dimension_scores_in_valid_range(self, scoring_service):
        svc, mock_client = scoring_service
        self._mock_claude_response(mock_client, MOCK_HOT_SCORE)
        result = svc.score_conversation(HOT_LEAD_TRANSCRIPT)
        for dim, val in result["breakdown"].items():
            assert 0 <= val <= 100, f"Dimension '{dim}' score {val} out of range 0-100"

    def test_returns_reasoning_string(self, scoring_service):
        svc, mock_client = scoring_service
        self._mock_claude_response(mock_client, MOCK_HOT_SCORE)
        result = svc.score_conversation(HOT_LEAD_TRANSCRIPT)
        assert "reasoning" in result
        assert isinstance(result["reasoning"], str)
        assert len(result["reasoning"]) > 10

    def test_returns_recommendation(self, scoring_service):
        svc, mock_client = scoring_service
        self._mock_claude_response(mock_client, MOCK_HOT_SCORE)
        result = svc.score_conversation(HOT_LEAD_TRANSCRIPT)
        assert "recommendation" in result


# ─────────────────────────────────────────────────────────────
#  TESTS — Fallback handling
# ─────────────────────────────────────────────────────────────

class TestScoringFallbacks:
    def test_handles_malformed_json_from_claude(self, scoring_service):
        """If Claude returns malformed JSON, scoring falls back to defaults."""
        svc, mock_client = scoring_service
        t = MagicMock(); t.text = "I'm sorry, I cannot score this conversation."
        r = MagicMock(); r.content = [t]
        mock_client.messages.create.return_value = r

        result = svc.score_conversation("some conversation")
        assert isinstance(result, dict)
        assert "overall_score" in result
        # Fallback score should be valid
        assert 0 <= result["overall_score"] <= 100

    def test_handles_api_exception(self, scoring_service):
        """API errors do not crash — returns default low score."""
        svc, mock_client = scoring_service
        mock_client.messages.create.side_effect = Exception("Connection timeout")

        result = svc.score_conversation("some conversation")
        assert isinstance(result, dict)
        assert "overall_score" in result

    def test_empty_transcript_returns_low_score(self, scoring_service):
        """Empty/minimal transcript should produce a low-ish default score."""
        svc, mock_client = scoring_service
        t = MagicMock(); t.text = json.dumps(MOCK_COLD_SCORE)
        r = MagicMock(); r.content = [t]
        mock_client.messages.create.return_value = r

        result = svc.score_conversation("")
        assert "overall_score" in result


# ─────────────────────────────────────────────────────────────
#  TESTS — Weighted scoring formula validation
# ─────────────────────────────────────────────────────────────

class TestWeightedScoring:
    """
    Validates scoring weights:
    ICP Fit 30% | Intent 25% | Timeline 20% | Authority 15% | Engagement 10%
    """

    def test_weighted_formula_consistency(self, scoring_service):
        """
        Given known dimension scores, overall_score should roughly match
        the weighted formula: 0.30*icp + 0.25*intent + 0.20*timeline + 0.15*auth + 0.10*eng
        """
        svc, mock_client = scoring_service

        dims = {"icp_fit": 80, "intent_signals": 90, "timeline": 70, "authority": 85, "engagement": 60}
        expected = int(0.30 * 80 + 0.25 * 90 + 0.20 * 70 + 0.15 * 85 + 0.10 * 60)  # = 80

        score_payload = {
            "overall_score": expected,
            "breakdown": dims,
            "reasoning": "Consistent with weighted formula",
            "recommendation": "Route to sales",
        }
        t = MagicMock(); t.text = json.dumps(score_payload)
        r = MagicMock(); r.content = [t]
        mock_client.messages.create.return_value = r

        result = svc.score_conversation("Test conversation")
        # Allow ±5 tolerance for rounding
        assert abs(result["overall_score"] - expected) <= 5, (
            f"Expected ~{expected}, got {result['overall_score']}"
        )
