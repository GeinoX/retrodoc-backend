from django.urls import path
from .views import RegionList, StationList

urlpatterns = [
    path("regions/", RegionList.as_view()),
    path("stations/", StationList.as_view()),
]