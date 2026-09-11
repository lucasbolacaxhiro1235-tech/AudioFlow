import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger(__name__)


def _send_smtp(to_email: str, subject: str, html: str) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = to_email
        msg.attach(MIMEText(html, "html", "utf-8"))

        if settings.SMTP_USE_SSL:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            if settings.SMTP_USE_TLS:
                server.starttls()

        if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)

        server.sendmail(settings.SMTP_FROM_EMAIL, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as exc:
        logger.warning("Failed to send email to %s: %s", to_email, exc)
        return False


def _base_template(title: str, body: str) -> str:
    return f"""<html>
<body style="margin:0;padding:0;background:#0a0a0a;color:#ffffff;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <div style="max-width:480px;margin:0 auto;padding:40px 24px;">
    <h1 style="font-size:22px;margin:0 0 8px;">AudioFlow</h1>
    <p style="font-size:16px;color:#a3a3a3;margin:0 0 24px;">{title}</p>
    <div style="background:#141414;border:1px solid #262626;border-radius:12px;padding:24px;">
      {body}
    </div>
    <p style="font-size:12px;color:#525252;margin-top:24px;">Se você não solicitou isto, pode ignorar este e-mail.</p>
  </div>
</body>
</html>"""


def send_verification_email(to_email: str, token: str) -> bool:
    url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    body = f"""
      <p style="margin:0 0 16px;">Confirme seu endereço de e-mail clicando no botão abaixo.</p>
      <a href="{url}" style="display:inline-block;background:#1db954;color:#ffffff;text-decoration:none;padding:12px 24px;border-radius:8px;font-weight:600;">Confirmar e-mail</a>
      <p style="margin:16px 0 0;font-size:13px;color:#a3a3a3;">O link expira em 24 horas.</p>
    """
    return _send_smtp(to_email, "Confirme seu e-mail — AudioFlow", _base_template("Verificação de e-mail", body))


def send_password_reset_email(to_email: str, token: str) -> bool:
    url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    body = f"""
      <p style="margin:0 0 16px;">Clique no botão abaixo para redefinir sua senha.</p>
      <a href="{url}" style="display:inline-block;background:#1db954;color:#ffffff;text-decoration:none;padding:12px 24px;border-radius:8px;font-weight:600;">Redefinir senha</a>
      <p style="margin:16px 0 0;font-size:13px;color:#a3a3a3;">O link expira em 1 hora.</p>
    """
    return _send_smtp(to_email, "Redefina sua senha — AudioFlow", _base_template("Redefinição de senha", body))


def send_email(to_email: str, subject: str, body: str) -> bool:
    return _send_smtp(to_email, subject, _base_template(subject, body))