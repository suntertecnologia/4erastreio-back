from fastapi import APIRouter, Depends, status
from src.notification import notification_handler
from src.auth.auth_handler import get_current_user
from src.db.models import Usuario

router = APIRouter()


@router.post("/send-notifications", status_code=status.HTTP_202_ACCEPTED)
def send_notifications(current_user: Usuario = Depends(get_current_user)):
    notification_handler.process_pending_notifications(current_user.id)
    return {"message": "Notification process initiated in the background."}
