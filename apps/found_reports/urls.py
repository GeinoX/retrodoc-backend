from django.urls import path

from .views import (
    DropOffConfirmView,
    FoundReportCreateView,
    MyFoundReportsView,
)

urlpatterns = [
    path(
        "",
        FoundReportCreateView.as_view(),
        name="found-report-create",
    ),

    path(
        "my/",
        MyFoundReportsView.as_view(),
        name="my-found-reports",
    ),

    path(
        "drop-off/confirm/",
        DropOffConfirmView.as_view(),
        name="drop-off-confirm",
    ),
]