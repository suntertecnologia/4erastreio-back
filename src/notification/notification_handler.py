import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from src.notification import notification_crud
from src.db import database, models
from src.configs.logger_config import logger
from src.utils.html_email_constructor import build_email_html
from datetime import datetime
from collections import defaultdict


def send_notification_email(subject: str, message: str, to_email: str):
    """Envia e-mail SOMENTE em HTML via SMTP."""
    import os
    from email.header import Header
    from dotenv import load_dotenv

    load_dotenv()
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = os.getenv("SMTP_PORT")
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

    if not all([SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD]):
        logger.error(
            "Missing one or more SMTP environment variables for email notification."
        )
        return

    # Somente HTML
    msg = MIMEText(message, "html", "utf-8")
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = Header(subject, "utf-8")

    try:
        with smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT)) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, [to_email], msg.as_string())
        logger.info(f"Email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Error sending email: {e}")


def get_status_emoji(entrega: models.Entrega):
    if entrega.status and ("entregue" in entrega.status.lower()):
        return "Entregue 🟢"
    elif entrega.previsao_entrega or entrega.previsao_entrega < datetime.now().date():
        return "Em atraso 🔴"
    return "Em andamento 🔵"


def process_pending_notifications(user_id: int):
    """Processes all pending notifications."""
    load_dotenv()
    SMTP_USER = os.getenv("SMTP_USER")
    LOGO_URL = os.getenv("LOGO_URL")
    COMPANY_NAME = os.getenv("COMPANY_NAME")
    db: Session = database.SessionLocal()
    try:
        pending_notifications = notification_crud.get_pending_notifications(db)
        if not pending_notifications:
            logger.info("No pending notifications to process.")
            return

        deliveries_by_carrier = defaultdict(list)
        for mov in pending_notifications:
            entrega = (
                db.query(models.Entrega)
                .filter(models.Entrega.id == mov.entrega_id)
                .first()
            )
            if entrega:
                deliveries_by_carrier[entrega.transportadora].append(entrega)

        now = datetime.now()
        html_email = build_email_html(
            deliveries_by_carrier,
            now,
            get_status_emoji,
            logo_url=LOGO_URL,
            company_name=COMPANY_NAME,
        )

        send_notification_email("Atualização de Entregas", html_email, SMTP_USER)

        log = notification_crud.create_notification_log(
            db, detalhes=html_email, status="enviado", entrega_id=None, user_id=user_id
        )

        for mov in pending_notifications:
            notification_crud.update_movimentacao_notificacao(
                db, mov.id, log.id, "notificado"
            )

        logger.info(
            f"{len(pending_notifications)} notifications processed successfully."
        )

    except Exception as e:
        logger.error(
            f"An error occurred during notification processing: {e}", exc_info=True
        )
    finally:
        db.close()
