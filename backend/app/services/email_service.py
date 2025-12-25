"""Email service for sending verification and notification emails."""
import os
import logging
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import secrets
from datetime import datetime, timezone, timedelta
import hashlib

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending emails using SMTP.

    Supports:
    - Email verification
    - Password reset
    - Notifications
    """

    def __init__(self):
        """Initialize email service with SMTP configuration."""
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("FROM_NAME", "LifeAI")
        self.app_url = os.getenv("APP_URL", "http://localhost:3000")

        self.enabled = bool(self.smtp_user and self.smtp_password)

        if not self.enabled:
            logger.warning(
                "Email service not configured. Set SMTP_USER and SMTP_PASSWORD "
                "environment variables to enable email functionality."
            )

    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email using SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text email body (fallback)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info(f"[EMAIL DISABLED] Would send to {to_email}: {subject}")
            logger.debug(f"Content: {html_content[:200]}...")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            # Add text and HTML parts
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)

            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}", exc_info=True)
            return False

    def send_verification_email(
        self,
        to_email: str,
        verification_token: str,
        user_name: Optional[str] = None
    ) -> bool:
        """
        Send email verification link.

        Args:
            to_email: User email address
            verification_token: Verification token
            user_name: Optional user name

        Returns:
            True if sent successfully
        """
        verification_url = f"{self.app_url}/verify-email?token={verification_token}"
        greeting = f"Cześć {user_name}!" if user_name else "Cześć!"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Witaj w LifeAI!</h1>
                </div>
                <div class="content">
                    <p>{greeting}</p>

                    <p>Dziękujemy za rejestrację w LifeAI - Twoim osobistym asystencie AI do zarządzania życiem!</p>

                    <p>Aby aktywować swoje konto i zacząć korzystać z wszystkich funkcji, kliknij poniższy przycisk:</p>

                    <div style="text-align: center;">
                        <a href="{verification_url}" class="button">Zweryfikuj adres email</a>
                    </div>

                    <p>Lub skopiuj i wklej ten link do przeglądarki:</p>
                    <p style="background: #fff; padding: 10px; border-left: 3px solid #667eea; word-break: break-all;">
                        {verification_url}
                    </p>

                    <p><strong>Link weryfikacyjny wygasa za 24 godziny.</strong></p>

                    <p>Jeśli nie rejestrowałeś się w LifeAI, zignoruj tę wiadomość.</p>

                    <p>Pozdrawiamy,<br>Zespół LifeAI</p>
                </div>
                <div class="footer">
                    <p>LifeAI - Twój inteligentny asystent życia</p>
                    <p>To jest automatyczna wiadomość. Nie odpowiadaj na ten email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        {greeting}

        Dziękujemy za rejestrację w LifeAI!

        Aby aktywować swoje konto, kliknij w link:
        {verification_url}

        Link weryfikacyjny wygasa za 24 godziny.

        Jeśli nie rejestrowałeś się w LifeAI, zignoruj tę wiadomość.

        Pozdrawiamy,
        Zespół LifeAI
        """

        return self._send_email(
            to_email=to_email,
            subject="Zweryfikuj swój adres email - LifeAI",
            html_content=html_content,
            text_content=text_content
        )

    def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str,
        user_name: Optional[str] = None
    ) -> bool:
        """
        Send password reset link.

        Args:
            to_email: User email address
            reset_token: Password reset token
            user_name: Optional user name

        Returns:
            True if sent successfully
        """
        reset_url = f"{self.app_url}/reset-password?token={reset_token}"
        greeting = f"Cześć {user_name}!" if user_name else "Cześć!"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #f5576c; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .warning {{ background: #fff3cd; border-left: 3px solid #ffc107; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Resetowanie hasła</h1>
                </div>
                <div class="content">
                    <p>{greeting}</p>

                    <p>Otrzymaliśmy prośbę o zresetowanie hasła do Twojego konta LifeAI.</p>

                    <p>Aby ustawić nowe hasło, kliknij poniższy przycisk:</p>

                    <div style="text-align: center;">
                        <a href="{reset_url}" class="button">Zresetuj hasło</a>
                    </div>

                    <p>Lub skopiuj i wklej ten link do przeglądarki:</p>
                    <p style="background: #fff; padding: 10px; border-left: 3px solid #f5576c; word-break: break-all;">
                        {reset_url}
                    </p>

                    <div class="warning">
                        <strong>⚠️ Ważne informacje bezpieczeństwa:</strong>
                        <ul>
                            <li>Link resetowania hasła wygasa za 1 godzinę</li>
                            <li>Link może być użyty tylko jeden raz</li>
                            <li>Jeśli nie prosiłeś o reset hasła, zignoruj tę wiadomość</li>
                        </ul>
                    </div>

                    <p>Jeśli nie rejestrowałeś prośby o reset hasła, Twoje konto może być zagrożone. W takim przypadku zalecamy natychmiastową zmianę hasła.</p>

                    <p>Pozdrawiamy,<br>Zespół LifeAI</p>
                </div>
                <div class="footer">
                    <p>LifeAI - Twój inteligentny asystent życia</p>
                    <p>To jest automatyczna wiadomość. Nie odpowiadaj na ten email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        {greeting}

        Otrzymaliśmy prośbę o zresetowanie hasła do Twojego konta LifeAI.

        Aby ustawić nowe hasło, kliknij w link:
        {reset_url}

        WAŻNE:
        - Link resetowania wygasa za 1 godzinę
        - Link może być użyty tylko jeden raz
        - Jeśli nie prosiłeś o reset hasła, zignoruj tę wiadomość

        Pozdrawiamy,
        Zespół LifeAI
        """

        return self._send_email(
            to_email=to_email,
            subject="Resetowanie hasła - LifeAI",
            html_content=html_content,
            text_content=text_content
        )

    @staticmethod
    def generate_verification_token() -> str:
        """
        Generate secure verification token.

        Returns:
            URL-safe verification token
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_password_reset_token() -> str:
        """
        Generate secure password reset token.

        Returns:
            URL-safe reset token
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_token(token: str) -> str:
        """
        Hash a token for secure storage.

        Args:
            token: Plain token

        Returns:
            Hashed token
        """
        return hashlib.sha256(token.encode()).hexdigest()


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """
    Get singleton email service instance.

    Returns:
        EmailService instance
    """
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
