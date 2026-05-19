"""
SendGrid email client for price alert notifications.
Swap-ready: set SENDGRID_API_KEY in .env to enable real emails.
If the key is 'placeholder' or empty, falls back to console logging.
"""
from __future__ import annotations

from app.config import get_settings

settings = get_settings()

FROM_EMAIL = "alerts@skymind.dev"
FROM_NAME  = "SkyMind Alerts"


def send_price_alert_email(
    to_email: str,
    to_name: str,
    origin_iata: str,
    destination_iata: str,
    target_price_usd: float,
    current_price_usd: float,
) -> bool:
    """
    Send a price drop alert email to the user.
    Returns True if sent (or logged), False on error.

    Real mode  : SENDGRID_API_KEY set to a real key in .env
    Mock mode  : key is 'placeholder' — logs to console instead
    """
    subject = (
        f"Price Alert: {origin_iata} → {destination_iata} "
        f"dropped to ${current_price_usd:.2f}"
    )
    body = (
        f"Hi {to_name},\n\n"
        f"Good news! The price for your watched route has dropped.\n\n"
        f"Route:         {origin_iata} → {destination_iata}\n"
        f"Your target:   ${target_price_usd:.2f}\n"
        f"Current price: ${current_price_usd:.2f}\n\n"
        f"Log in to SkyMind to book before the price changes.\n\n"
        f"— The SkyMind Team"
    )

    api_key = settings.SENDGRID_API_KEY
    if not api_key or api_key == "placeholder":
        return _mock_send(to_email, subject, body)
    return _real_send(to_email, subject, body, api_key)


def _mock_send(to_email: str, subject: str, body: str) -> bool:
    print(f"[SendGrid MOCK] To: {to_email}")
    print(f"[SendGrid MOCK] Subject: {subject}")
    print(f"[SendGrid MOCK] Body:\n{body}")
    return True


def _real_send(to_email: str, subject: str, body: str, api_key: str) -> bool:
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        message = Mail(
            from_email=(FROM_EMAIL, FROM_NAME),
            to_emails=to_email,
            subject=subject,
            plain_text_content=body,
        )
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print(f"[SendGrid] Sent to {to_email} — status {response.status_code}")
        return response.status_code in (200, 202)
    except Exception as e:
        print(f"[SendGrid] ERROR sending to {to_email}: {e}")
        return False