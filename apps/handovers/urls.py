from django.urls import path

from .views import (
    MyHandoverAttemptsView,
    OfficerRefuseHandoverView,
)


urlpatterns = [
    path(
        "my/",
        MyHandoverAttemptsView.as_view(),
        name="my-handover-attempts",
    ),
    path(
        "officer/refuse/",
        OfficerRefuseHandoverView.as_view(),
        name="officer-refuse-handover",
    ),
]