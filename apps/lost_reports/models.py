import uuid

from django.conf import settings
from django.db import models

from apps.documents.models import DocumentCategory
from apps.found_reports.models import FoundReport
from apps.stations.models import Region


class LostReport(models.Model):
    class Status(models.TextChoices):
        SEARCHING = "searching", "Searching"
        POSSIBLE_MATCH = "possible_match", "Possible match"
        AWAITING_COLLECTION = "awaiting_collection", "Awaiting collection"
        COLLECTED = "collected", "Collected"
        CLOSED = "closed", "Closed"
        EXPIRED = "expired", "Expired"

    reference = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="lost_reports",
    )

    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.PROTECT,
        related_name="lost_reports",
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
        related_name="lost_reports",
        null=True,
        blank=True,
    )

    place_detail = models.CharField(max_length=300, blank=True)

    date_lost = models.DateField()

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.SEARCHING,
    )

    matched_found_report = models.ForeignKey(
        FoundReport,
        on_delete=models.PROTECT,
        related_name="matched_lost_reports",
        null=True,
        blank=True,
    )

    collection_code = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
    )

    collection_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="collections_handled",
        null=True,
        blank=True,
    )

    officer_confirmed = models.BooleanField(default=False)
    owner_confirmed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.reference}"