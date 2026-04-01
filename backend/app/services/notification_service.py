"""Notification helpers for submission confirmation messages."""
import smtplib
from email.message import EmailMessage

from app.core.config import (
    EMAIL_FROM,
    EMAIL_PROVIDER,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USE_TLS,
    SMTP_USERNAME,
)


def send_submission_confirmation_email(
    *,
    recipient_email: str,
    assignment_title: str,
    file_count: int,
    replacement_status: str,
) -> None:
    """Send a submission confirmation email when provider configuration allows.

    Provider modes:
    - none: no-op
    - smtp: send using configured SMTP server
    """
    if EMAIL_PROVIDER == "none":
        return

    if EMAIL_PROVIDER != "smtp":
        raise ValueError(f"Unsupported EMAIL_PROVIDER: {EMAIL_PROVIDER}")

    if not EMAIL_FROM:
        raise ValueError("EMAIL_FROM must be configured when EMAIL_PROVIDER=smtp")
    if not SMTP_HOST:
        raise ValueError("SMTP_HOST must be configured when EMAIL_PROVIDER=smtp")

    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = recipient_email
    msg["Subject"] = f"Submission received: {assignment_title}"
    msg.set_content(
        "\n".join(
            [
                "Your submission was received successfully.",
                f"Assignment: {assignment_title}",
                f"Files processed: {file_count}",
                f"Submission type: {replacement_status}",
            ]
        )
    )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as smtp:
        if SMTP_USE_TLS:
            smtp.starttls()
        if SMTP_USERNAME:
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        smtp.send_message(msg)
