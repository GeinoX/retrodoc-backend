from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CustomUser
from apps.notifications.tasks import send_verification_email
from .verification_service import VerificationService

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True);

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "password"]
        read_only_fields = ['id']

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A User with this email already exists, so try another")
        return value.lower() if value else value

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data, role=CustomUser.RoleChoices.CITIZEN, email_verified=False, password=password)
        verification_token = VerificationService.generate_token(user)
        verification_url = VerificationService.build_verification_url(verification_token)
        send_verification_email.delay(
        user.id,
        verification_url
    )
        return user
        
    
