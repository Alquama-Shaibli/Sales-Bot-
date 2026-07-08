"""
conftest.py — Shared pytest configuration and fixtures
Automatically loaded by pytest before any test file.
"""
import pytest
import sys
import os

# Ensure backend/ is on PYTHONPATH for all tests
sys.path.insert(0, os.path.dirname(__file__))


# ── Shared markers ────────────────────────────────────────────
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with -m 'not slow')")
    config.addinivalue_line("markers", "integration: marks tests requiring external APIs")
    config.addinivalue_line("markers", "unit: marks pure unit tests (no I/O)")


# ── Shared fixtures ───────────────────────────────────────────
@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    """Set environment variables for the entire test session."""
    os.environ.setdefault("ANTHROPIC_API_KEY",  "test-key-for-ci")
    os.environ.setdefault("DATABASE_URL",       "sqlite:///:memory:")
    os.environ.setdefault("HUBSPOT_API_KEY",    "")
    os.environ.setdefault("TWILIO_ACCOUNT_SID", "")
    os.environ.setdefault("TWILIO_AUTH_TOKEN",  "")
    os.environ.setdefault("SENDGRID_API_KEY",   "")
    os.environ.setdefault("SALES_EMAIL",        "")
    os.environ.setdefault("DEBUG",              "True")
    yield
