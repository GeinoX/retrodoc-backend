from django.urls import path

from .views import (
    MarkAllNotificationsReadView,
    MarkNotificationReadView,
    MyNotificationsView,
    UnreadNotificationCountView,
    UnreadNotificationsView,
)


urlpatterns = [
    path(
        "",
        MyNotificationsView.as_view(),
        name="my-notifications",
    ),

    path(
        "unread/",
        UnreadNotificationsView.as_view(),
        name="unread-notifications",
    ),

    path(
        "unread/count/",
        UnreadNotificationCountView.as_view(),
        name="unread-notification-count",
    ),

    path(
        "read-all/",
        MarkAllNotificationsReadView.as_view(),
        name="mark-all-notifications-read",
    ),

    path(
        "<int:pk>/read/",
        MarkNotificationReadView.as_view(),
        name="mark-notification-read",
    ),
]