from django.conf import settings

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegistrationSerializer
from .verification_service import VerificationService


COOKIE = "refresh_token"
COOKIE_PATH = "/api/v1/auth/"

COOKIE_OPTIONS = {
    "httponly": True,
    "secure": not settings.DEBUG,
    "samesite": "Lax",
    "path": COOKIE_PATH,
    "max_age": 7 * 24 * 3600,
}


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Student registered successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        token = request.query_params.get("token")

        if not token:
            return Response(
                {"detail": "Verification token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = VerificationService.verify_token(token)

        if not user:
            return Response(
                {"detail": "Invalid or expired verification token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        VerificationService.mark_email_verified(user)

        return Response(
            {"detail": "Email verified successfully."},
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):
    """
    Anyone with a valid account email and password can log in.

    Email verification is NOT required for login.
    Login throttling is disabled for the prototype.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = TokenObtainPairSerializer(
            data={
                "email": request.data.get("email"),
                "password": request.data.get("password"),
            }
        )

        serializer.is_valid(raise_exception=True)

        tokens = serializer.validated_data

        response = Response(
            {
                "access": tokens["access"],
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            COOKIE,
            tokens["refresh"],
            **COOKIE_OPTIONS,
        )

        return response


class RefreshView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get(COOKIE, "")

        serializer = TokenRefreshSerializer(
            data={
                "refresh": refresh_token,
            }
        )

        try:
            serializer.is_valid(raise_exception=True)
        except (TokenError, ValidationError):
            return Response(
                {"detail": "Session expired"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        data = serializer.validated_data

        response = Response(
            {
                "access": data["access"],
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            COOKIE,
            data["refresh"],
            **COOKIE_OPTIONS,
        )

        return response


class LogoutView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        token = request.COOKIES.get(COOKIE)

        if token:
            try:
                RefreshToken(token).blacklist()
            except TokenError:
                pass

        response = Response(status=status.HTTP_204_NO_CONTENT)

        response.delete_cookie(
            COOKIE,
            path=COOKIE_PATH,
            samesite="Lax",
        )

        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response(
            {
                "id": user.pk,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "role": user.role,
                "email_verified": user.email_verified,
            },
            status=status.HTTP_200_OK,
        )

    from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

