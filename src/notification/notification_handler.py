import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from src.notification import notification_crud
from src.db import database, models
from src.configs.logger_config import logger
from src.utils.html_email_constructor import build_email_html
from datetime import datetime
from collections import defaultdict
import requests


def send_notification_email(subject: str, html_body: str, to_email: str, region="us"):
    MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
    API_KEY = os.getenv("MAILGUN_API_KEY")  # Private key (key-xxxx)
    base = (
        "https://api.mailgun.net/v3"
        if region == "us"
        else "https://api.eu.mailgun.net/v3"
    )
    url = f"{base}/{MAILGUN_DOMAIN}/messages"
    data = {
        "from": f"postmaster@{MAILGUN_DOMAIN}",
        "to": to_email,
        "subject": subject,
        "html": html_body,
    }
    try:
        r = requests.post(url, auth=("api", API_KEY), data=data, timeout=20)
        logger.info(f"Email sent successfully to {to_email} {r.json()} {r.text}")
    except Exception as e:
        logger.error(f"Error sending email: {e}")


def get_status_emoji(entrega: models.Entrega):
    if entrega.status and ("entregue" in entrega.status.lower()):
        return "Entregue 🟢"
    elif entrega.previsao_entrega and entrega.previsao_entrega < datetime.now().date():
        return "Em atraso 🔴"
    return "Em andamento 🔵"


def process_pending_notifications(user_id: int):
    """Processes all pending notifications."""
    load_dotenv()
    SMTP_USER = os.getenv("SMTP_USER")
    LOGO_URL = os.getenv("LOGO_URL")
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
            deliveries_by_carrier, now, get_status_emoji, logo_url=LOGO_URL
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
