"""
services/hubspot_service.py — HubSpot CRM Integration
Syncs qualified leads to HubSpot as contacts with custom fields.
Handles create-or-update logic to avoid duplicates.
"""
import logging
import requests
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings

logger = logging.getLogger(__name__)

HUBSPOT_BASE_URL = "https://api.hubapi.com"


class HubSpotService:
    """
    Client for HubSpot CRM API.
    Creates/updates contacts and sets custom lead qualification properties.
    """

    def __init__(self):
        self.api_key = settings.hubspot_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if not self.api_key:
            logger.warning("⚠️  HubSpot API key not set — sync will be skipped")

    def _is_configured(self) -> bool:
        return bool(self.api_key and self.api_key != "")

    # ── Contact Lookup ────────────────────────────────────────────────────────

    def get_contact_by_email(self, email: str) -> Optional[str]:
        """
        Look up a HubSpot contact by email.
        Returns the contact ID if found, None otherwise.
        """
        if not self._is_configured() or not email:
            return None
        try:
            url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts/search"
            payload = {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "email",
                        "operator": "EQ",
                        "value": email,
                    }]
                }],
                "properties": ["email", "firstname", "lastname"],
                "limit": 1,
            }
            resp = requests.post(url, json=payload, headers=self.headers, timeout=10)
            resp.raise_for_status()
            results = resp.json().get("results", [])
            if results:
                contact_id = results[0]["id"]
                logger.info(f"Found existing HubSpot contact: {contact_id}")
                return contact_id
        except Exception as e:
            logger.error(f"HubSpot contact lookup failed: {e}")
        return None

    # ── Contact Create ────────────────────────────────────────────────────────

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=5))
    def create_contact(self, properties: Dict[str, Any]) -> Optional[str]:
        """Create a new HubSpot contact. Returns contact ID."""
        if not self._is_configured():
            return None
        try:
            url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts"
            payload = {"properties": properties}
            resp = requests.post(url, json=payload, headers=self.headers, timeout=10)
            resp.raise_for_status()
            contact_id = resp.json()["id"]
            logger.info(f"✅ HubSpot contact created: {contact_id}")
            return contact_id
        except requests.HTTPError as e:
            if e.response.status_code == 409:
                logger.warning("Contact already exists in HubSpot (409)")
                return None
            raise

    # ── Contact Update ────────────────────────────────────────────────────────

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=5))
    def update_contact(self, contact_id: str, properties: Dict[str, Any]) -> bool:
        """Update an existing HubSpot contact's properties."""
        if not self._is_configured():
            return False
        try:
            url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts/{contact_id}"
            payload = {"properties": properties}
            resp = requests.patch(url, json=payload, headers=self.headers, timeout=10)
            resp.raise_for_status()
            logger.info(f"✅ HubSpot contact updated: {contact_id}")
            return True
        except Exception as e:
            logger.error(f"HubSpot update failed: {e}")
            return False

    # ── Main Sync Function ────────────────────────────────────────────────────

    async def sync_lead(self, lead, request) -> Optional[str]:
        """
        Main sync function — creates or updates a HubSpot contact.

        Maps lead data to HubSpot standard + custom properties:
        - Standard: email, firstname, lastname, company, jobtitle
        - Custom: lead_score, icp_fit, intent_level, timeline, conversation_id
        """
        if not self._is_configured():
            logger.info("HubSpot not configured — skipping sync")
            return None

        # Determine intent level string
        intent_str = "Unknown"
        if lead.intent_level:
            intent_str = lead.intent_level.value if hasattr(lead.intent_level, "value") else str(lead.intent_level)

        # Build HubSpot properties
        properties = {
            # Standard fields
            "email": lead.email or "",
            "firstname": lead.first_name or "",
            "lastname": lead.last_name or "",
            "company": lead.company or "",
            "jobtitle": lead.job_title or "",
            # Custom qualification fields
            "lead_score": str(lead.score),
            "icp_fit": str(lead.icp_fit),
            "intent_level": intent_str,
            "timeline": lead.timeline or "",
            "conversation_id": str(lead.conversation_id),
            "qualification_date": "",  # Will be set by HubSpot timestamp
        }

        # Check if contact already exists
        existing_id = self.get_contact_by_email(lead.email) if lead.email else None

        if existing_id:
            # Update existing contact
            self.update_contact(existing_id, properties)
            return existing_id
        else:
            # Create new contact
            return self.create_contact(properties)

    # ── Add Note ──────────────────────────────────────────────────────────────

    def add_note(self, contact_id: str, note_body: str) -> bool:
        """Add a conversation note to a HubSpot contact."""
        if not self._is_configured():
            return False
        try:
            url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/notes"
            payload = {
                "properties": {
                    "hs_note_body": note_body,
                    "hs_timestamp": str(int(__import__("time").time() * 1000)),
                },
                "associations": [{
                    "to": {"id": contact_id},
                    "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 202}],
                }],
            }
            resp = requests.post(url, json=payload, headers=self.headers, timeout=10)
            resp.raise_for_status()
            logger.info(f"Note added to HubSpot contact {contact_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add HubSpot note: {e}")
            return False
