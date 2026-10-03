from celery import shared_task

from apps.accounts.models import CustomUser
from apps.notifications.services.email_service import EmailService


@shared_task
def send_verification_email(
    user_id,
    verification_url,
):
    user = CustomUser.objects.get(
        id=user_id
    )

    EmailService.send_verification_email(
        user=user,
        verification_url=verification_url,
    )