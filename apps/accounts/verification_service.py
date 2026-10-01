from django.core import signing
from django.urls import reverse

from apps.accounts.models import CustomUser


class VerificationService:
    TOKEN_SALT = "email-verification"
    TOKEN_MAX_AGE = 60 * 60 * 24  # 24 hours

    @classmethod
    def generate_token(cls, user):
        payload = {
            "user_id": user.id,
            "email": user.email,
        }

        return signing.dumps(
            payload,
            salt=cls.TOKEN_SALT
        )

    @classmethod
    def build_verification_url(cls, token):
        path = reverse("verify-email")

        return f"http://127.0.0.1:8000/api/v1{path}?token={token}"

    @classmethod
    def verify_token(cls, token):
        try:
            payload = signing.loads(
                token,
                salt=cls.TOKEN_SALT,
                max_age=cls.TOKEN_MAX_AGE,
            )
        except signing.BadSignature:
            return None
        except signing.SignatureExpired:
            return None

        try:
            user = CustomUser.objects.get(
                id=payload["user_id"],
                email=payload["email"],
            )
        except CustomUser.DoesNotExist:
            return None

        return user

    @classmethod
    def mark_email_verified(cls, user):
        if user.email_verified:
            return user

        user.email_verified = True
        user.save(update_fields=["email_verified"])

        return user