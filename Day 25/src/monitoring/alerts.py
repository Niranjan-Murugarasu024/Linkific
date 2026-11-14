"""Optional SMTP alert helper. No email is sent unless SMTP settings are configured."""
import os
import smtplib
from email.message import EmailMessage


def send_failure_alert(subject: str, body: str) -> bool:
    host = os.getenv("SMTP_HOST")
    sender = os.getenv("ALERT_FROM")
    recipient = os.getenv("ALERT_TO")
    if not all([host, sender, recipient]):
        return False
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient
    message.set_content(body)
    port = int(os.getenv("SMTP_PORT", "587"))
    with smtplib.SMTP(host, port, timeout=20) as server:
        server.starttls()
        username = os.getenv("SMTP_USER")
        password = os.getenv("SMTP_PASSWORD")
        if username and password:
            server.login(username, password)
        server.send_message(message)
    return True
