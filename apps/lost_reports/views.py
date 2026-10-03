import secrets

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.administration.permissions import IsOfficerOrAdmin
from apps.found_reports.models import FoundReport
from apps.handovers.models import HandoverAttempt
from apps.matching.matching import find_matches
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

        report.matched_found_report = found_report
        report.status = LostReport.Status.POSSIBLE_MATCH

        report.save(
            update_fields=[
                "matched_found_report",
                "status",
                "updated_at",
            ]
        )

        if found_report.status == FoundReport.Status.AT_STATION:
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
            )
        )


class ConfirmMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, reference):
        try:
            report = (
                LostReport.objects
                .select_related(
                    "owner",
                    "matched_found_report",
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
                    "detail": (
                        "No matched found report exists."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        report.collection_code = generate_collection_code()
        report.status = (
            LostReport.Status.AWAITING_COLLECTION
        )

        report.save(
            update_fields=[
                "collection_code",
                "status",
                "updated_at",
            ]
        )

        found_report = report.matched_found_report

        if (
            found_report.status
            != FoundReport.Status.OWNER_MAY_BE_FOUND
        ):
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
                "You confirmed the possible document match. "
                "Take your collection code and proof of identity "
                "to the station."
            ),
            notification_type=Notification.Type.ACTION,
            reference=report.reference,
        )

        notify(
            user=found_report.finder,
            title="Owner identified",
            message=(
                "The owner of the document you found has "
                "confirmed a possible match. The document "
                "remains at the station until collection "
                "is completed."
            ),
            notification_type=Notification.Type.STATUS,
            reference=found_report.reference,
        )

        return Response(
            {
                "detail": "Match confirmed.",
                "status": report.status,
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
                        "This report does not have a "
                        "pending possible match."
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
                "Your lost report remains active."
            ),
            notification_type=Notification.Type.STATUS,
            reference=report.reference,
        )

        return Response(
            {
                "detail": "Possible match rejected.",
                "status": report.status,
            },
            status=status.HTTP_200_OK,
        )


class OfficerConfirmCollectionView(APIView):
    permission_classes = [IsOfficerOrAdmin]

    def post(self, request):
        collection_code = (
            request.data.get("collection_code") or ""
        ).strip().upper()

        proof_shown = (
            request.data.get("proof_shown") or ""
        ).strip()

        note = (
            request.data.get("note") or ""
        ).strip()

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
                        "Collection has already been confirmed "
                        "by an officer."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        report.collection_officer = request.user
        report.officer_confirmed = True

        attempt_number = (
            report.handover_attempts.count() + 1
        )

        HandoverAttempt.objects.create(
            lost_report=report,
            officer=request.user,
            result=HandoverAttempt.Result.RELEASED,
            proof_shown=proof_shown,
            note=note,
            attempt_number=attempt_number,
        )

        completed = complete_collection(report)

        if not completed:
            report.save(
                update_fields=[
                    "collection_officer",
                    "officer_confirmed",
                    "updated_at",
                ]
            )

        notify(
            user=report.owner,
            title="Station verification completed",
            message=(
                "The station officer has verified your "
                "collection details."
            ),
            notification_type=Notification.Type.STATUS,
            reference=report.reference,
        )

        if completed:
            notify(
                user=report.owner,
                title="Document collected",
                message=(
                    "Your document collection has been "
                    "completed successfully."
                ),
                notification_type=Notification.Type.STATUS,
                reference=report.reference,
            )

            if report.matched_found_report:
                notify(
                    user=report.matched_found_report.finder,
                    title="Document returned",
                    message=(
                        "The document you found has been "
                        "successfully returned to its owner."
                    ),
                    notification_type=Notification.Type.STATUS,
                    reference=(
                        report.matched_found_report.reference
                    ),
                )

        return Response(
            {
                "detail": (
                    "Officer collection confirmation recorded."
                ),
                "status": report.status,
                "officer_confirmed": (
                    report.officer_confirmed
                ),
                "owner_confirmed": (
                    report.owner_confirmed
                ),
            },
            status=status.HTTP_200_OK,
        )


class OwnerConfirmCollectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, reference):
        try:
            report = (
                LostReport.objects
                .select_related(
                    "owner",
                    "matched_found_report",
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
                        "Collection has already been confirmed "
                        "by the owner."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        report.owner_confirmed = True

        completed = complete_collection(report)

        if not completed:
            report.save(
                update_fields=[
                    "owner_confirmed",
                    "updated_at",
                ]
            )

        if completed:
            notify(
                user=request.user,
                title="Document collected",
                message=(
                    "Your document collection has been "
                    "completed successfully."
                ),
                notification_type=Notification.Type.STATUS,
                reference=report.reference,
            )

            if report.matched_found_report:
                notify(
                    user=report.matched_found_report.finder,
                    title="Document returned",
                    message=(
                        "The document you found has been "
                        "successfully returned to its owner."
                    ),
                    notification_type=Notification.Type.STATUS,
                    reference=(
                        report.matched_found_report.reference
                    ),
                )

        else:
            notify(
                user=request.user,
                title="Collection confirmation recorded",
                message=(
                    "Your collection confirmation has been "
                    "recorded. The station officer still needs "
                    "to complete their confirmation."
                ),
                notification_type=Notification.Type.STATUS,
                reference=report.reference,
            )

        return Response(
            {
                "detail": (
                    "Owner collection confirmation recorded."
                ),
                "status": report.status,
                "officer_confirmed": (
                    report.officer_confirmed
                ),
                "owner_confirmed": (
                    report.owner_confirmed
                ),
            },
            status=status.HTTP_200_OK,
        )