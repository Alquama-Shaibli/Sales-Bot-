"""
services/alert_service.py — Hot Lead Alert System
Sends real-time SMS (Twilio) + Email (SendGrid) alerts
when a lead scores 75+ on the qualification engine.
Gracefully degrades if keys not configured.
"""
import logging
from typing import Optional
from datetime import datetime

from config import settings

logger = logging.getLogger(__name__)


# ── Safe imports (optional dependencies) ─────────────────────
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("Twilio not installed — SMS alerts disabled")

try:
    import sendgrid
    from sendgrid.helpers.mail import Mail, To, From, Subject, PlainTextContent, HtmlContent
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    logger.warning("SendGrid not installed — email alerts disabled")


# ────────────────────────────────────────────────────────────
#  SMS ALERT
# ────────────────────────────────────────────────────────────

class SMSAlerter:
    """Sends SMS via Twilio when a hot lead is detected."""

    def __init__(self):
        self.enabled = (
            TWILIO_AVAILABLE
            and bool(settings.twilio_account_sid)
            and bool(settings.twilio_auth_token)
            and bool(settings.twilio_phone_from)
            and bool(settings.sales_alert_phone)
        )
        if self.enabled:
            self.client = TwilioClient(
                settings.twilio_account_sid,
                settings.twilio_auth_token,
            )
        else:
            logger.info("SMS alerts disabled — Twilio not configured")

    def send(self, lead) -> bool:
        """Send a hot lead SMS alert. Returns True if sent."""
        if not self.enabled:
            return False

        score   = getattr(lead, 'score', 0)
        email   = getattr(lead, 'email', 'Unknown')
        company = getattr(lead, 'company', 'Unknown company')
        name    = f"{getattr(lead, 'first_name', '') or ''} {getattr(lead, 'last_name', '') or ''}".strip() or "Unknown"

        message_body = (
            f"🔴 HOT LEAD ALERT — EnterpriseLead AI\n\n"
            f"Score: {score}/100\n"
            f"Name:  {name}\n"
            f"Email: {email}\n"
            f"Co:    {company}\n"
            f"Time:  {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
            f"→ Route to sales immediately!"
        )

        try:
            msg = self.client.messages.create(
                body=message_body,
                from_=settings.twilio_phone_from,
                to=settings.sales_alert_phone,
            )
            logger.info(f"✅ SMS sent: SID={msg.sid} to {settings.sales_alert_phone}")
            return True
        except Exception as e:
            logger.error(f"SMS send failed: {e}")
            return False


# ────────────────────────────────────────────────────────────
#  EMAIL ALERT
# ────────────────────────────────────────────────────────────

class EmailAlerter:
    """Sends email via SendGrid when a hot lead is detected."""

    def __init__(self):
        self.enabled = (
            SENDGRID_AVAILABLE
            and bool(settings.sendgrid_api_key)
            and bool(settings.sales_email)
        )
        if self.enabled:
            self.client = sendgrid.SendGridAPIClient(api_key=settings.sendgrid_api_key)
        else:
            logger.info("Email alerts disabled — SendGrid not configured")

    def _build_html(self, lead, score_data: Optional[dict] = None) -> str:
        """Build a rich HTML email body."""
        score   = getattr(lead, 'score', 0)
        email   = getattr(lead, 'email', 'Not provided')
        company = getattr(lead, 'company', 'Unknown')
        name    = f"{getattr(lead, 'first_name', '') or ''} {getattr(lead, 'last_name', '') or ''}".strip() or "Unknown"
        title   = getattr(lead, 'job_title', 'Unknown') or 'Unknown'
        ts      = datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')

        # Build dimension rows if available
        dim_rows = ""
        if score_data and score_data.get("breakdown"):
            bd = score_data["breakdown"]
            dims = [
                ("ICP Fit",        bd.get("icp_fit", "—"),        "30%"),
                ("Intent Signals", bd.get("intent_signals", "—"), "25%"),
                ("Timeline",       bd.get("timeline", "—"),       "20%"),
                ("Authority",      bd.get("authority", "—"),      "15%"),
                ("Engagement",     bd.get("engagement", "—"),     "10%"),
            ]
            for dim, val, weight in dims:
                dim_rows += f"""
                <tr>
                  <td style="padding:6px 12px;color:#94a3b8;font-size:13px;">{dim} <span style="color:#475569">({weight})</span></td>
                  <td style="padding:6px 12px;font-weight:700;color:#ef4444;text-align:right;">{val}/100</td>
                </tr>"""

        reasoning = (score_data or {}).get("reasoning", "")

        return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#0a0f1e;font-family:Inter,Arial,sans-serif;">
  <div style="max-width:520px;margin:40px auto;background:#0f1629;border:1px solid rgba(255,255,255,0.1);border-radius:16px;overflow:hidden;">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#ef4444,#f59e0b);padding:24px 28px;">
      <div style="font-size:28px;margin-bottom:4px;">🔴 Hot Lead Alert</div>
      <div style="color:rgba(255,255,255,0.9);font-size:14px;">EnterpriseLead AI — Immediate Action Required</div>
    </div>

    <!-- Score Badge -->
    <div style="padding:24px 28px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.08);">
      <div style="display:inline-block;background:rgba(239,68,68,0.15);border:2px solid rgba(239,68,68,0.4);border-radius:50%;width:80px;height:80px;line-height:80px;font-size:28px;font-weight:800;color:#f87171;">{score}</div>
      <div style="color:#94a3b8;font-size:13px;margin-top:8px;">Lead Score / 100</div>
    </div>

    <!-- Lead Details -->
    <div style="padding:20px 28px;">
      <table style="width:100%;border-collapse:collapse;">
        <tr><td style="padding:6px 0;color:#94a3b8;font-size:13px;width:100px;">Name</td><td style="padding:6px 0;color:#f0f4ff;font-weight:600;">{name}</td></tr>
        <tr><td style="padding:6px 0;color:#94a3b8;font-size:13px;">Email</td><td style="padding:6px 0;color:#60a5fa;">{email}</td></tr>
        <tr><td style="padding:6px 0;color:#94a3b8;font-size:13px;">Company</td><td style="padding:6px 0;color:#f0f4ff;font-weight:600;">{company}</td></tr>
        <tr><td style="padding:6px 0;color:#94a3b8;font-size:13px;">Title</td><td style="padding:6px 0;color:#f0f4ff;">{title}</td></tr>
        <tr><td style="padding:6px 0;color:#94a3b8;font-size:13px;">Qualified</td><td style="padding:6px 0;color:#f0f4ff;">{ts}</td></tr>
      </table>
    </div>

    <!-- Score Breakdown -->
    {f'''<div style="padding:0 28px 20px;">
      <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:4px 0;">
        <div style="padding:10px 12px;color:#64748b;font-size:11px;letter-spacing:0.08em;font-weight:600;">SCORE BREAKDOWN</div>
        <table style="width:100%;border-collapse:collapse;">{dim_rows}</table>
      </div>
    </div>''' if dim_rows else ''}

    <!-- Reasoning -->
    {f'''<div style="padding:0 28px 20px;">
      <div style="background:rgba(79,142,247,0.08);border:1px solid rgba(79,142,247,0.2);border-radius:10px;padding:14px;">
        <div style="color:#64748b;font-size:11px;font-weight:600;letter-spacing:0.08em;margin-bottom:6px;">💡 AI REASONING</div>
        <div style="color:#94a3b8;font-size:13px;line-height:1.6;">{reasoning}</div>
      </div>
    </div>''' if reasoning else ''}

    <!-- CTA -->
    <div style="padding:20px 28px 28px;text-align:center;">
      <div style="background:linear-gradient(135deg,#ef4444,#f59e0b);border-radius:10px;padding:14px 28px;display:inline-block;color:white;font-weight:700;font-size:15px;">
        🚀 Route to Sales Team Immediately
      </div>
    </div>

    <!-- Footer -->
    <div style="padding:16px 28px;border-top:1px solid rgba(255,255,255,0.06);text-align:center;">
      <div style="color:#475569;font-size:11px;">EnterpriseLead AI · FlowZint Hackathon 2026 · Powered by Claude AI</div>
    </div>
  </div>
</body>
</html>"""

    def send(self, lead, score_data: Optional[dict] = None) -> bool:
        """Send a hot lead email alert. Returns True if sent."""
        if not self.enabled:
            return False

        email   = getattr(lead, 'email', None)
        company = getattr(lead, 'company', 'Unknown')
        score   = getattr(lead, 'score', 0)

        try:
            message = Mail(
                from_email=From("alerts@enterpriselead.ai", "EnterpriseLead AI"),
                to_emails=To(settings.sales_email),
                subject=Subject(f"🔴 HOT LEAD: {company} — Score {score}/100"),
                plain_text_content=PlainTextContent(
                    f"Hot Lead Alert!\n\nScore: {score}/100\nEmail: {email}\nCompany: {company}\n"
                    f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\nRoute to sales immediately!"
                ),
                html_content=HtmlContent(self._build_html(lead, score_data)),
            )

            response = self.client.send(message)
            logger.info(f"✅ Email sent: status={response.status_code} to {settings.sales_email}")
            return response.status_code in (200, 202)

        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False


# ────────────────────────────────────────────────────────────
#  MAIN ALERT SERVICE
# ────────────────────────────────────────────────────────────

class AlertService:
    """
    Orchestrates all alert channels for hot leads.
    Usage:
        svc = AlertService()
        await svc.send_hot_lead_alert(lead, score_data)
    """

    def __init__(self):
        self.sms   = SMSAlerter()
        self.email = EmailAlerter()

    async def send_hot_lead_alert(self, lead, score_data: Optional[dict] = None) -> dict:
        """
        Send alerts through all configured channels.
        Non-blocking — failures are logged but don't crash the request.
        Returns dict with channel statuses.
        """
        if not lead or getattr(lead, 'score', 0) < settings.lead_score_threshold:
            return {"sms": False, "email": False, "reason": "Score below threshold"}

        results = {
            "sms":   False,
            "email": False,
            "score": getattr(lead, 'score', 0),
            "channels_tried": [],
        }

        # SMS
        if self.sms.enabled:
            results["channels_tried"].append("sms")
            results["sms"] = self.sms.send(lead)
        else:
            logger.info("⏭️  SMS skipped — not configured")

        # Email
        if self.email.enabled:
            results["channels_tried"].append("email")
            results["email"] = self.email.send(lead, score_data)
        else:
            logger.info("⏭️  Email skipped — not configured")

        # Summary log
        if not results["channels_tried"]:
            logger.warning(
                f"⚠️  Hot lead score={results['score']} — no alert channels configured. "
                f"Set TWILIO_* or SENDGRID_* env vars to enable."
            )
        else:
            success = results["sms"] or results["email"]
            logger.info(
                f"{'✅' if success else '⚠️'} Alert for score={results['score']}: "
                f"SMS={'✓' if results['sms'] else '✗'}  "
                f"Email={'✓' if results['email'] else '✗'}"
            )

        return results

    def is_configured(self) -> dict:
        """Check which alert channels are active."""
        return {
            "sms_enabled":   self.sms.enabled,
            "email_enabled": self.email.enabled,
            "threshold":     settings.lead_score_threshold,
        }
