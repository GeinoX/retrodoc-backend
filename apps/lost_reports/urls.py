from django.urls import path

from .views import (
    ConfirmMatchView,
    LostReportCreateView,
    MyLostReportsView,
    OfficerConfirmCollectionView,
    OwnerConfirmCollectionView,
    RejectMatchView,
)

urlpatterns = [
    path(
        "",
        LostReportCreateView.as_view(),
        name="lost-report-create",
    ),

    path(
        "my/",
        MyLostReportsView.as_view(),
        name="my-lost-reports",
    ),

    path(
        "<uuid:reference>/confirm/",
        ConfirmMatchView.as_view(),
        name="confirm-match",
    ),

    path(
        "<uuid:reference>/reject/",
        RejectMatchView.as_view(),
        name="reject-match",
    ),

    path(
        "collection/officer-confirm/",
        OfficerConfirmCollectionView.as_view(),
        name="officer-confirm-collection",
    ),

    path(
        "<uuid:reference>/collection/owner-confirm/",
        OwnerConfirmCollectionView.as_view(),
        name="owner-confirm-collection",
    ),
]