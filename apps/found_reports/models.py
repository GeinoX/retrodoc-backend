import uuid

from django.conf import settings
from django.db import models

from apps.documents.models import DocumentCategory
from apps.stations.models import Region, Station


class FoundReport(models.Model):
    class Status(models.TextChoices):
        AWAITING_DROP_OFF = "awaiting_drop_off", "Awaiting drop-off"
        AT_STATION = "at_station", "At the station"
        OWNER_MAY_BE_FOUND = "owner_may_be_found", "Owner may be found"
        RETURNED_TO_OWNER = "returned_to_owner", "Returned to owner"
        UNCLAIMED = "unclaimed", "Unclaimed"
        DROP_OFF_DECLINED = "drop_off_declined", "Drop-off declined"

    reference = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    finder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="found_reports",
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.PROTECT,
        related_name="found_reports",
    )

    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.PROTECT,
        related_name="found_reports",
    )

    title = models.CharField(max_length=200)

    name_on_document = models.CharField(max_length=200, blank=True)
    document_number = models.CharField(max_length=200, blank=True)

    date_of_birth = models.DateField(null=True, blank=True)
    issue_date = models.DateField(null=True, blank=True)

    issuing_organisation = models.CharField(max_length=200, blank=True)

    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="found_reports",
        null=True,
        blank=True,
    )

    place_detail = models.CharField(max_length=300, blank=True)

    date_found = models.DateField()

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.AWAITING_DROP_OFF,
    )

    drop_off_code = models.CharField(
        max_length=20,
        unique=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.reference}"