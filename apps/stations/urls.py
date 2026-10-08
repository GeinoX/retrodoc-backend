from django.urls import path

from .views import RegionList, StationList


urlpatterns = [
    path(
        "regions/",
        RegionList.as_view(),
        name="regions",
    ),

    path(
        "",
        StationList.as_view(),
        name="stations",
    ),
]