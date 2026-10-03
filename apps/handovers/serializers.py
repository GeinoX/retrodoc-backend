from rest_framework import serializers

from .models import HandoverAttempt


class HandoverAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = HandoverAttempt

        fields = [
            "id",
            "lost_report",
            "officer",
            "result",
            "proof_shown",
            "note",
            "attempt_number",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "lost_report",
            "officer",
            "attempt_number",
            "created_at",
        ]