import os
import smtplib
from email.message import EmailMessage

from business_object.notification import Notification


class EmailNotifier:
    """Sends notifications by email through an SMTP server."""

    def __init__(self):
        # Credentials come from environment variables, never from the code
        self.host = os.environ["SMTP_HOST"]  # e.g. smtp.gmail.com
        self.port = int(os.environ.get("SMTP_PORT", 587))
        self.username = os.environ["SMTP_USER"]
        self.password = os.environ["SMTP_PASSWORD"]
        self.sender = os.environ.get("SMTP_SENDER", self.username)

    def send(self, notification: Notification, to_email: str) -> bool:
        """Returns True if the email was sent, False otherwise."""
        msg = EmailMessage()
        msg["Subject"] = "NEO alert: an object is approaching Earth"
        msg["From"] = self.sender
        msg["To"] = to_email
        msg.set_content(notification.message)

        try:
            with smtplib.SMTP(self.host, self.port, timeout=10) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            return True
        except (smtplib.SMTPException, OSError) as e:
            print(f"Email sending failed for {to_email}: {e}")
            return False
