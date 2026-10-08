import secrets

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.administration.permissions import IsOfficerOrAdmin
from apps.found_reports.models import FoundReport
from apps.handovers.models import HandoverAttempt
from apps.matching.services import find_matches, apply_match
from apps.notifications.models import Notification
from apps.notifications.services.notification_service import notify

from .models import LostReport
from .serializers import LostReportSerializer


def generate_collection_code():
    return secrets.token_hex(4).upper()


def complete_collection(report):
    """
    Complete collection when both the officer and owner
    have confirmed the handover.
    """

    if not (
        report.officer_confirmed
        and report.owner_confirmed
    ):
        return False

    report.status = LostReport.Status.COLLECTED

    report.save(
        update_fields=[
            "status",
            "collection_officer",
            "officer_confirmed",
            "owner_confirmed",
            "updated_at",
        ]
    )

    found_report = report.matched_found_report

    if found_report:
        found_report.status = (
            FoundReport.Status.RETURNED_TO_OWNER
        )

        found_report.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    return True


class LostReportCreateView(generics.CreateAPIView):
    serializer_class = LostReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        report = serializer.save(
            owner=self.request.user
        )

        notify(
            user=self.request.user,
            title="Lost report submitted",
            message=(
                "Your lost document report has been submitted "
                "and is now being searched."
            ),
            notification_type=Notification.Type.STATUS,
            reference=report.reference,
        )

        matches = find_matches(report)

        if not matches:
            return

        found_report = matches[0]

        apply_match(report, found_report)

        notify(
            user=self.request.user,
            title="Possible document match",
            message=(
                "We found a document that may match your lost "
                "document. Please review the details and "
                "confirm if it is yours."
            ),
            notification_type=Notification.Type.MATCH,
            reference=report.reference,
        )


class MyLostReportsView(generics.ListAPIView):
    serializer_class = LostReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            LostReport.objects
            .filter(owner=self.request.user)
            .select_related(
                "category",
                "region",
                "matched_found_report",
                "matched_found_report__station",
            )
        )


class ConfirmMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, reference):
        try:
            report = (
                LostReport.objects
                .select_related(
                    "matched_found_report",
                    "matched_found_report__station",
                )
                .get(
                    reference=reference,
                    owner=request.user,
                )
            )
        except LostReport.DoesNotExist:
            return Response(
                {
                    "detail": "Lost report not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if report.status != LostReport.Status.POSSIBLE_MATCH:
            return Response(
                {
                    "detail": (
                        "This report does not currently "
                        "have a possible match."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not report.matched_found_report:
            return Response(
                {
                    "detail": "No matched document is available."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        report.collection_code = generate_collection_code()
        report.status = LostReport.Status.AWAITING_COLLECTION

        report.save(
            update_fields=[
                "collection_code",
                "status",
                "updated_at",
            ]
        )

        found_report = report.matched_found_report

        found_report.status = (
            FoundReport.Status.OWNER_MAY_BE_FOUND
        )

        found_report.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        notify(
            user=request.user,
            title="Match confirmed",
            message=(
                "The possible match has been confirmed. "
                "Please visit the station with your "
                "collection code and required proof."
            ),
            notification_type=Notification.Type.MATCH,
            reference=report.reference,
        )

        notify(
            user=found_report.finder,
            title="Possible owner identified",
            message=(
                "A possible owner has confirmed a match "
                "for a document you reported."
            ),
            notification_type=Notification.Type.MATCH,
            reference=report.reference,
        )

        return Response(
            {
                "detail": "Match confirmed.",
                "report": LostReportSerializer(
                    report
                ).data,
                "collection_code": report.collection_code,
            },
            status=status.HTTP_200_OK,
        )


class RejectMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, reference):
        try:
            report = LostReport.objects.get(
                reference=reference,
                owner=request.user,
            )
        except LostReport.DoesNotExist:
            return Response(
                {
                    "detail": "Lost report not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if report.status != LostReport.Status.POSSIBLE_MATCH:
            return Response(
                {
                    "detail": (
                        "This report does not currently "
                        "have a possible match."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        report.matched_found_report = None
        report.status = LostReport.Status.SEARCHING

        report.save(
            update_fields=[
                "matched_found_report",
                "status",
                "updated_at",
            ]
        )

        notify(
            user=request.user,
            title="Match rejected",
            message=(
                "The possible match was rejected. "
                "Your lost document will continue to be searched."
            ),
            notification_type=Notification.Type.STATUS,
            reference=report.reference,
        )

        return Response(
            {
                "detail": "Match rejected.",
                "report": LostReportSerializer(
                    report
                ).data,
            },
            status=status.HTTP_200_OK,
        )


class OfficerConfirmCollectionView(APIView):
    permission_classes = [IsOfficerOrAdmin]

    def post(self, request):
        collection_code = (
            request.data.get("collection_code") or ""
        ).strip().upper()

        if not collection_code:
            return Response(
                {
                    "detail": "Collection code is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            report = (
                LostReport.objects
                .select_related(
                    "owner",
                    "matched_found_report",
                )
                .get(
                    collection_code=collection_code
                )
            )
        except LostReport.DoesNotExist:
            return Response(
                {
                    "detail": "Invalid collection code."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if report.status != LostReport.Status.AWAITING_COLLECTION:
            return Response(
                {
                    "detail": (
                        "This report is not awaiting collection."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if report.officer_confirmed:
            return Response(
                {
                    "detail": (
                        "Officer collection has already "
                        "been confirmed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        report.collection_officer = request.user
        report.officer_confirmed = True

        report.save(
            update_fields=[
                "collection_officer",
                "officer_confirmed",
                "updated_at",
            ]
        )

        attempt_number = (
            report.handover_attempts.count() + 1
        )

        HandoverAttempt.objects.create(
            lost_report=report,
            officer=request.user,
            result=HandoverAttempt.Result.RELEASED,
            attempt_number=attempt_number,
        )

        completed = complete_collection(report)

        notify(
            user=report.owner,
            title="Collection confirmed",
            message=(
                "The station has confirmed the collection "
                "process for your document."
            ),
            notification_type=Notification.Type.STATUS,
            reference=report.reference,
        )

        if completed and report.matched_found_report:
            notify(
                user=report.matched_found_report.finder,
                title="Document collected",
                message=(
                    "The document you reported has been "
                    "collected by the confirmed owner."
                ),
                notification_type=Notification.Type.STATUS,
                reference=report.reference,
            )

        return Response(
            {
                "detail": (
                    "Collection confirmed by officer."
                ),
                "completed": completed,
                "report": LostReportSerializer(
                    report
                ).data,
            },
            status=status.HTTP_200_OK,
        )


class OwnerConfirmCollectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, reference):
        try:
            report = LostReport.objects.get(
                reference=reference,
                owner=request.user,
            )
        except LostReport.DoesNotExist:
            return Response(
                {
                    "detail": "Lost report not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if report.status != LostReport.Status.AWAITING_COLLECTION:
            return Response(
                {
                    "detail": (
                        "This report is not awaiting collection."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if report.owner_confirmed:
            return Response(
                {
                    "detail": (
                        "Owner collection has already "
                        "been confirmed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        report.owner_confirmed = True

        report.save(
            update_fields=[
                "owner_confirmed",
                "updated_at",
            ]
        )

        completed = complete_collection(report)

        notify(
            user=request.user,
            title="Collection confirmed",
            message=(
                "Your collection confirmation has been recorded."
            ),
            notification_type=Notification.Type.STATUS,
            reference=report.reference,
        )

        return Response(
            {
                "detail": "Collection confirmed by owner.",
                "completed": completed,
                "report": LostReportSerializer(
                    report
                ).data,
            },
            status=status.HTTP_200_OK,
        )

