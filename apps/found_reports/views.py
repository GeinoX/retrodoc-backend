from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.administration.permissions import IsOfficerOrAdmin
from apps.lost_reports.models import LostReport
from apps.matching.matching import reports_match
from apps.notifications.models import Notification
from apps.notifications.services.notification_service import notify

from .models import FoundReport
from .serializers import FoundReportSerializer


class FoundReportCreateView(generics.CreateAPIView):
    serializer_class = FoundReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        report = serializer.save(
            finder=self.request.user
        )

        notify(
            user=self.request.user,
            title="Found report submitted",
            message=(
                "Your found document report has been submitted. "
                "Please take the document to the selected station "
                "and keep your drop-off code."
            ),
            notification_type=Notification.Type.STATUS,
            reference=report.reference,
        )


class MyFoundReportsView(generics.ListAPIView):
    serializer_class = FoundReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            FoundReport.objects
            .filter(finder=self.request.user)
            .select_related(
                "station",
                "category",
                "region",
            )
        )


class DropOffConfirmView(APIView):
    permission_classes = [IsOfficerOrAdmin]

    def post(self, request):
        drop_off_code = (
            request.data.get("drop_off_code") or ""
        ).strip().upper()

        if not drop_off_code:
            return Response(
                {
                    "detail": "Drop-off code is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            report = (
                FoundReport.objects
                .select_related(
                    "finder",
                    "category",
                    "station",
                )
                .get(
                    drop_off_code=drop_off_code
                )
            )
        except FoundReport.DoesNotExist:
            return Response(
                {
                    "detail": "Invalid drop-off code."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if report.status != FoundReport.Status.AWAITING_DROP_OFF:
            return Response(
                {
                    "detail": (
                        "This report cannot be dropped off "
                        "in its current status."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        report.status = FoundReport.Status.AT_STATION

        report.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        notify(
            user=report.finder,
            title="Document received",
            message=(
                "The station has confirmed receipt of "
                "the document you found."
            ),
            notification_type=Notification.Type.STATUS,
            reference=report.reference,
        )

        lost_reports = (
            LostReport.objects
            .filter(
                status=LostReport.Status.SEARCHING
            )
            .select_related(
                "owner",
                "category",
            )
        )

        matched_reports = []

        for lost_report in lost_reports:
            if reports_match(
                lost_report,
                report,
            ):
                matched_reports.append(
                    lost_report
                )

        for lost_report in matched_reports:
            lost_report.matched_found_report = report
            lost_report.status = (
                LostReport.Status.POSSIBLE_MATCH
            )

            lost_report.save(
                update_fields=[
                    "matched_found_report",
                    "status",
                    "updated_at",
                ]
            )

            notify(
                user=lost_report.owner,
                title="Possible document match",
                message=(
                    "A document matching your lost report "
                    "may have been found. Please review your "
                    "report and confirm if it is yours."
                ),
                notification_type=Notification.Type.MATCH,
                reference=lost_report.reference,
            )

        if matched_reports:
            report.status = (
                FoundReport.Status.OWNER_MAY_BE_FOUND
            )

            report.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        return Response(
            {
                "detail": (
                    "Document drop-off confirmed."
                ),
                "status": report.status,
                "possible_matches": len(
                    matched_reports
                ),
            },
            status=status.HTTP_200_OK,
        )