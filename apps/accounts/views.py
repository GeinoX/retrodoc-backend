from django.shortcuts import render
from .serializers import RegistrationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .verification_service import VerificationService
from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken


# Create your views here.

class RegisterView(APIView):

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Student registered successfully"})
        return Response(serializer.errors, status=400)

class VerifyEmailView(APIView):

    def get(self, request):
        token = request.query_params.get("token")

        if not token:
            return Response(
                {"detail": "Verification token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = VerificationService.verify_token(token)

        if not user:
            return Response(
                {"detail": "Invalid or expired verification token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        VerificationService.mark_email_verified(user)

        return Response(
            {"detail": "Email verified successfully."},
            status=status.HTTP_200_OK
        )

COOKIE = "refresh_token"
COOKIE_PATH = "/api/v1/auth/"  # use your real prefix
COOKIE_OPTIONS = {
    "httponly": True,                 # scripts cannot read it
    "secure": not settings.DEBUG,     # HTTPS only in production
    "samesite": "Lax",
    "path": COOKIE_PATH,
    "max_age": 7 * 24 * 3600,
}


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        serializer = TokenObtainPairSerializer(data=request.data)  # expects email + password
        serializer.is_valid(raise_exception=True)
        tokens = serializer.validated_data
        response = Response({"access": tokens["access"]})
        response.set_cookie(COOKIE, tokens["refresh"], **COOKIE_OPTIONS)
        return response


class RefreshView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = TokenRefreshSerializer(data={"refresh": request.COOKIES.get(COOKIE, "")})
        try:
            serializer.is_valid(raise_exception=True)
        except (TokenError, ValidationError):
            return Response({"detail": "Session expired"}, status=401)
        data = serializer.validated_data
        response = Response({"access": data["access"]})
        response.set_cookie(COOKIE, data["refresh"], **COOKIE_OPTIONS)
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
        response = Response(status=204)
        response.delete_cookie(COOKIE, path=COOKIE_PATH, samesite="Lax")
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({
            "id": u.pk,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "role": u.role,
            "email_verified": u.email_verified,
        })