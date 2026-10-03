from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


class MyNotificationsView(generics.ListAPIView):
    """
    Return notifications belonging to the authenticated user.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        )


class UnreadNotificationsView(generics.ListAPIView):
    """
    Return only unread notifications.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user,
            is_read=False,
        )


class MarkNotificationReadView(APIView):
    """
    Mark one notification as read.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            notification = Notification.objects.get(
                pk=pk,
                user=request.user,
            )
        except Notification.DoesNotExist:
            return Response(
                {
                    "detail": "Notification not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        notification.is_read = True
        notification.save(
            update_fields=["is_read"]
        )

        return Response(
            {
                "detail": "Notification marked as read."
            },
            status=status.HTTP_200_OK,
        )


class MarkAllNotificationsReadView(APIView):
    """
    Mark all notifications belonging to the
    authenticated user as read.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request):
        updated = Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).update(
            is_read=True,
        )

        return Response(
            {
                "detail": "Notifications marked as read.",
                "updated": updated,
            },
            status=status.HTTP_200_OK,
        )


class UnreadNotificationCountView(APIView):
    """
    Return the number of unread notifications.

    Useful for the frontend notification badge.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).count()

        return Response(
            {
                "count": count,
            }
        )