from fastapi import BackgroundTasks
from src.notification import notification_handler


def schedule_notifications(background_tasks: BackgroundTasks, user_id: int):
    background_tasks.add_task(
        notification_handler.process_pending_notifications, user_id
    )
    return {"message": "Notification process initiated in the background."}
