from django.shortcuts import render
from .serializers import RegistrationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .verification_service import VerificationService


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
