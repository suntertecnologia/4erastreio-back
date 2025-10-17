from fastapi import APIRouter, Depends, status, BackgroundTasks
from src.notification import notification_service
from src.auth.auth_handler import get_current_user
from src.db.models import Usuario

router = APIRouter()


@router.post("/send-notifications", status_code=status.HTTP_202_ACCEPTED)
def send_notifications(
    background_tasks: BackgroundTasks,
    current_user: Usuario = Depends(get_current_user),
):
    return notification_service.schedule_notifications(
        background_tasks, current_user.id
    )
