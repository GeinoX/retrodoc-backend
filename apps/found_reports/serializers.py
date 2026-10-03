import secrets

from rest_framework import serializers

from .models import FoundReport


class FoundReportSerializer(serializers.ModelSerializer):
    reference = serializers.UUIDField(read_only=True)
    finder = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.CharField(read_only=True)
    drop_off_code = serializers.CharField(read_only=True)

    class Meta:
        model = FoundReport

        fields = [
            "reference",
            "finder",
            "station",
            "category",
            "title",
            "name_on_document",
            "document_number",
            "date_of_birth",
            "issue_date",
            "issuing_organisation",
            "region",
            "place_detail",
            "date_found",
            "status",
            "drop_off_code",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "reference",
            "finder",
            "status",
            "drop_off_code",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        validated_data["finder"] = self.context["request"].user
        validated_data["drop_off_code"] = secrets.token_hex(4).upper()

        return FoundReport.objects.create(**validated_data)