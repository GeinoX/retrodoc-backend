from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.administration.permissions import IsOfficerOrAdmin
from apps.lost_reports.models import LostReport

from .models import HandoverAttempt
from .serializers import HandoverAttemptSerializer


class MyHandoverAttemptsView(generics.ListAPIView):
    serializer_class = HandoverAttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            HandoverAttempt.objects
            .filter(lost_report__owner=self.request.user)
            .select_related(
                "lost_report",
                "officer",
            )
        )


class OfficerRefuseHandoverView(APIView):
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

        if not note:
            return Response(
                {
                    "detail": (
                        "A note is required when refusing "
                        "a handover."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            report = LostReport.objects.get(
                collection_code=collection_code
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

        attempt_number = (
            report.handover_attempts.count() + 1
        )

        attempt = HandoverAttempt.objects.create(
            lost_report=report,
            officer=request.user,
            result=HandoverAttempt.Result.REFUSED,
            proof_shown=proof_shown,
            note=note,
            attempt_number=attempt_number,
        )

        return Response(
            {
                "detail": (
                    "Handover refused and recorded."
                ),
                "attempt": HandoverAttemptSerializer(
                    attempt
                ).data,
            },
            status=status.HTTP_200_OK,
        )