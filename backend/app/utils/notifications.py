import smtplib
from email.message import EmailMessage

from app.core.config import get_settings


def send_email_alert(to_email: str, subject: str, message: str) -> None:
    settings = get_settings()

    email = EmailMessage()
    email["From"] = settings.alert_email_from
    email["To"] = to_email
    email["Subject"] = subject
    email.set_content(message)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_username and settings.smtp_password:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(email)
