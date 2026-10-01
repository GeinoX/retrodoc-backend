from django.urls import path
from .views import RegisterView, VerifyEmailView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/verify-email/", VerifyEmailView.as_view(), name="verify-email")
]
