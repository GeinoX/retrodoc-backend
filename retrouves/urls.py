from django.urls import path

from . import views

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("declarer/", views.declarer, name="declarer"),
        path("merci/<str:code>/", views.merci, name="merci"),
]