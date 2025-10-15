import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from src.notification import notification_crud
from src.db import database, models
from src.configs.logger_config import logger
from datetime import datetime
from collections import defaultdict


def send_notification_email(subject: str, message: str, to_email: str):
    """Sends a notification email using SMTP."""
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

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT))
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USER, to_email, text)
        server.quit()
        logger.info(f"Email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Error sending email: {e}")


def get_status_emoji(entrega: models.Entrega):
    if "entregue" in entrega.status.lower():
        return "Finalizado 🟢"
    elif entrega.previsao_entrega and entrega.previsao_entrega < datetime.now().date():
        return "Em atraso 🔴"
    elif entrega.previsao_entrega > entrega.previsao_entrega_inicial:
        return "Em atraso 🔴"
    return "Em andamento 🔵"


def process_pending_notifications(user_id: int):
    """Processes all pending notifications."""
    load_dotenv()
    SMTP_USER = os.getenv("SMTP_USER")
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
        message = "Olá, abaixo o resumo das suas entregas 🚚\n"
        message += (
            "-----------------------------------------------------------------\\n"
        )
        message += f"Status verificados em: {now.strftime("%d/%m/%Y às %H:%M")}\\n\\n"

        for carrier, deliveries in deliveries_by_carrier.items():
            message += f"{carrier.upper()}:\\n"
            for entrega in deliveries:
                message += f"Entrega: {entrega.codigo_rastreio}\\n"
                message += f"Cliente: {entrega.cliente}\\n"
                message += f"NF: {entrega.numero_nf}\\n"
                message += f"Status: {get_status_emoji(entrega)}\\n\\n"
                message += "Últimas movimentações\\n"
                if entrega.movimentacoes:
                    for mov in sorted(
                        entrega.movimentacoes,
                        key=lambda m: m.dt_movimento,
                        reverse=True,
                    )[:2]:
                        message += f"- {mov.movimento} | {mov.dt_movimento.strftime('%d/%m/%Y às %H:%M')}\\n"
                else:
                    message += "Sem novas movimentações\\n"
                message += "\\n-----------------------------------------------------------------------------------------------------------\\n\\n"

        send_notification_email("Atualização de Entregas", message, SMTP_USER)

        log = notification_crud.create_notification_log(
            db, detalhes=message, status="enviado", entrega_id=None, user_id=user_id
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
