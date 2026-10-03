from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        INFO = "info", "Information"
        MATCH = "match", "Possible match"
        STATUS = "status", "Status update"
        ACTION = "action", "Action required"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.INFO,
    )

    title = models.CharField(
        max_length=200,
    )

    message = models.TextField()

    # Reference to the related LostReport/FoundReport.
    # We keep this generic because a notification can refer
    # to different types of objects.
    reference = models.UUIDField(
        null=True,
        blank=True,
    )

    is_read = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email}: {self.title}"