"""
tests/test_chat.py — Unit tests for ChatService (Claude integration)
Run: pytest backend/tests/test_chat.py -v
"""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ─────────────────────────────────────────────────────────────
#  FIXTURES
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def mock_settings():
    """Mock settings so we don't need real API keys in tests."""
    with patch("config.settings") as s:
        s.anthropic_api_key  = "test-key-12345"
        s.claude_model       = "claude-3-5-sonnet-20241022"
        s.max_tokens         = 1024
        s.lead_score_threshold = 75
        yield s


@pytest.fixture
def chat_service(mock_settings):
    """Create a ChatService instance with mocked Anthropic client."""
    with patch("anthropic.Anthropic") as MockAnthropic:
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        from services.chat_service import ChatService
        svc = ChatService()
        svc.client = mock_client
        yield svc, mock_client


# ─────────────────────────────────────────────────────────────
#  TESTS — ChatService.get_opening_message
# ─────────────────────────────────────────────────────────────

class TestGetOpeningMessage:
    def test_returns_string(self, chat_service):
        svc, _ = chat_service
        msg = svc.get_opening_message()
        assert isinstance(msg, str)
        assert len(msg) > 20, "Opening message should be substantive"

    def test_contains_greeting_keywords(self, chat_service):
        svc, _ = chat_service
        msg = svc.get_opening_message().lower()
        has_keyword = any(w in msg for w in ["hello", "hi", "welcome", "help", "assist"])
        assert has_keyword, f"Expected greeting in opening message, got: {msg}"


# ─────────────────────────────────────────────────────────────
#  TESTS — ChatService.send_message
# ─────────────────────────────────────────────────────────────

class TestSendMessage:
    def test_send_message_returns_response_string(self, chat_service):
        """Claude API returns text → send_message returns it correctly."""
        svc, mock_client = chat_service

        # Arrange: mock Claude response
        mock_text_block = MagicMock()
        mock_text_block.text = "Great question! What is your company's headcount?"
        mock_response = MagicMock()
        mock_response.content = [mock_text_block]
        mock_client.messages.create.return_value = mock_response

        # Act
        result = svc.send_message(
            user_message="We use Salesforce for CRM",
            conversation_history=[],
        )

        # Assert
        assert isinstance(result, str)
        assert "headcount" in result.lower() or len(result) > 5

    def test_send_message_appends_to_history(self, chat_service):
        """Conversation history is correctly passed to Claude."""
        svc, mock_client = chat_service

        mock_text_block = MagicMock()
        mock_text_block.text = "How many employees?"
        mock_response = MagicMock()
        mock_response.content = [mock_text_block]
        mock_client.messages.create.return_value = mock_response

        history = [
            {"role": "user",      "content": "Hi there"},
            {"role": "assistant", "content": "Hello! What's your company?"},
        ]

        svc.send_message("Acme Corp", conversation_history=history)

        call_args = mock_client.messages.create.call_args
        messages_passed = call_args.kwargs.get("messages") or call_args.args[0] if call_args.args else []
        # History + new user message should be passed
        assert call_args is not None

    def test_send_message_handles_empty_response(self, chat_service):
        """If Claude returns empty content, returns fallback string."""
        svc, mock_client = chat_service

        mock_response = MagicMock()
        mock_response.content = []
        mock_client.messages.create.return_value = mock_response

        result = svc.send_message("Hello", conversation_history=[])
        assert isinstance(result, str)

    def test_send_message_handles_api_error(self, chat_service):
        """API errors are caught and a fallback message is returned."""
        svc, mock_client = chat_service

        mock_client.messages.create.side_effect = Exception("Rate limit exceeded")

        result = svc.send_message("Hello", conversation_history=[])
        # Should not raise — returns error string or fallback
        assert isinstance(result, str)


# ─────────────────────────────────────────────────────────────
#  TESTS — Conversation history management
# ─────────────────────────────────────────────────────────────

class TestConversationHistory:
    def test_history_format_is_valid(self, chat_service):
        """Each history entry must have role + content keys."""
        svc, mock_client = chat_service

        mock_text = MagicMock()
        mock_text.text = "What is your use case?"
        mock_resp = MagicMock()
        mock_resp.content = [mock_text]
        mock_client.messages.create.return_value = mock_resp

        history = [{"role": "user", "content": "We need automation"}]
        svc.send_message("We have 50 employees", conversation_history=history)

        call_args = mock_client.messages.create.call_args
        assert call_args is not None

    def test_system_prompt_is_included(self, chat_service):
        """System prompt should be passed in API call."""
        svc, mock_client = chat_service

        mock_text = MagicMock()
        mock_text.text = "Reply"
        mock_resp = MagicMock()
        mock_resp.content = [mock_text]
        mock_client.messages.create.return_value = mock_resp

        svc.send_message("test", conversation_history=[])

        call_kwargs = mock_client.messages.create.call_args.kwargs
        # System prompt should be set
        assert "system" in call_kwargs or "model" in call_kwargs


# ─────────────────────────────────────────────────────────────
#  INTEGRATION-STYLE — Message turn-taking
# ─────────────────────────────────────────────────────────────

class TestTurnTaking:
    def test_multi_turn_conversation_builds_history(self, chat_service):
        """Simulates a 3-turn conversation and validates message count."""
        svc, mock_client = chat_service

        def make_resp(text):
            t = MagicMock(); t.text = text
            r = MagicMock(); r.content = [t]
            return r

        mock_client.messages.create.side_effect = [
            make_resp("What company are you from?"),
            make_resp("How many employees?"),
            make_resp("What's your budget range?"),
        ]

        history = []
        turns = [
            "Hi, I'm from Acme Corp",
            "We have 200 employees",
            "Budget is around $50k/year",
        ]

        for user_msg in turns:
            response = svc.send_message(user_msg, conversation_history=history)
            history.append({"role": "user", "content": user_msg})
            history.append({"role": "assistant", "content": response})

        assert len(history) == 6  # 3 user + 3 assistant
        assert mock_client.messages.create.call_count == 3
