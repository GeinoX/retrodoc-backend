from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import HandoverAttempt


@admin.register(HandoverAttempt)
class HandoverAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "lost_report",
        "officer",
        "result",
        "attempt_number",
        "created_at",
    )

    list_filter = (
        "result",
        "created_at",
    )

    search_fields = (
        "lost_report__reference",
        "officer__email",
        "officer__first_name",
        "officer__last_name",
    )

    readonly_fields = (
        "created_at",
    )