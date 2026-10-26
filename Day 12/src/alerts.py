import os
import smtplib
from email.message import EmailMessage

from .config import logger


def send_failure_alert(error_message):
    enabled = (
        os.getenv("EMAIL_ALERTS_ENABLED", "false").lower()
        == "true"
    )

    if not enabled:
        logger.info("Email alerts are disabled")
        return

    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    recipient = os.getenv("ALERT_EMAIL_TO")

    if not all([host, username, password, recipient]):
        logger.error("SMTP configuration is incomplete")
        return

    message = EmailMessage()
    message["Subject"] = "ETL Pipeline Failure Alert"
    message["From"] = username
    message["To"] = recipient

    message.set_content(
        "The e-commerce ETL pipeline failed.\n\n"
        f"Error details:\n{error_message}"
    )

    try:
        with smtplib.SMTP(
            host,
            port,
            timeout=15,
        ) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(message)

        logger.info("Failure alert email sent")

    except Exception:
        logger.exception("Unable to send email alert")