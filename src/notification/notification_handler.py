import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from src.notification import notification_crud
from src.db import database
from src.configs.logger_config import logger


def send_notification_email(subject: str, message: str, to_email: str):
    """Sends a notification email using SMTP."""
    load_dotenv()
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = os.getenv("SMTP_PORT")
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    FROM_EMAIL = os.getenv("FROM_EMAIL")

    if not all([SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL]):
        logger.error(
            "Missing one or more SMTP environment variables for email notification."
        )
        return

    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT))
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(FROM_EMAIL, to_email, text)
        server.quit()
        logger.info(f"Email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Error sending email: {e}")


def process_pending_notifications(user_id: int):
    """Processes all pending notifications."""
    db: Session = database.SessionLocal()
    try:
        pending_notifications = notification_crud.get_pending_notifications(db)
        if not pending_notifications:
            logger.info("No pending notifications to process.")
            return

        message = ""
        for mov in pending_notifications:
            message += f"Entrega ID: {mov.entrega_id} - Status: {mov.status}\n"

        # In a real application, you would get the user's email from the database
        to_email = "user@example.com"
        send_notification_email("Atualização de Entregas", message, to_email)

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
