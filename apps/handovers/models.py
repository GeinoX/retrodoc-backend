from django.conf import settings
from django.db import models

from apps.lost_reports.models import LostReport


class HandoverAttempt(models.Model):
    class Result(models.TextChoices):
        RELEASED = "released", "Released"
        REFUSED = "refused", "Refused"

    lost_report = models.ForeignKey(
        LostReport,
        on_delete=models.PROTECT,
        related_name="handover_attempts",
    )

    officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="handover_attempts",
    )

    result = models.CharField(
        max_length=20,
        choices=Result.choices,
    )

    proof_shown = models.TextField(
        blank=True,
    )

    note = models.TextField(
        blank=True,
    )

    attempt_number = models.PositiveSmallIntegerField(
        default=1,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "lost_report",
                    "attempt_number",
                ],
                name="unique_handover_attempt_number",
            ),
        ]

    def __str__(self):
        return (
            f"{self.lost_report.reference} - "
            f"Attempt {self.attempt_number} - "
            f"{self.result}"
        )