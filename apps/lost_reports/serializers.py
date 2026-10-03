from rest_framework import serializers

from .models import LostReport


class LostReportSerializer(serializers.ModelSerializer):
    reference = serializers.UUIDField(read_only=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.CharField(read_only=True)

    matched_found_report = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    collection_code = serializers.CharField(read_only=True)

    collection_officer = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    officer_confirmed = serializers.BooleanField(read_only=True)
    owner_confirmed = serializers.BooleanField(read_only=True)

    class Meta:
        model = LostReport

        fields = [
            "reference",
            "owner",
            "category",
            "title",
            "name_on_document",
            "document_number",
            "date_of_birth",
            "issue_date",
            "issuing_organisation",
            "region",
            "place_detail",
            "date_lost",
            "status",
            "matched_found_report",
            "collection_code",
            "collection_officer",
            "officer_confirmed",
            "owner_confirmed",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "reference",
            "owner",
            "status",
            "matched_found_report",
            "collection_code",
            "collection_officer",
            "officer_confirmed",
            "owner_confirmed",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user

        return LostReport.objects.create(**validated_data)