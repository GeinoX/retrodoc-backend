from apps.notifications.models import Notification


def notify(
    user,
    title,
    message,
    notification_type=Notification.Type.INFO,
    reference=None,
):
    """
    Create an in-app notification for a user.

    This function does not send email.
    Email notifications are handled separately by EmailService.
    """

    if not user:
        return None

    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        reference=reference,
    )