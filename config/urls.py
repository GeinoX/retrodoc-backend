from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("retrouves.urls")),

    path("api/v1/", include("api.urls")),
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.stations.urls")),
    path("api/v1/", include("apps.documents.urls")),
    path("api/v1/", include("apps.found_reports.urls")),
    path("api/v1/", include("apps.lost_reports.urls")),
    path(
        "notifications/",
        include("apps.notifications.urls"),
    ),
    path(
    "handovers/",
    include("apps.handovers.urls"),
),
]