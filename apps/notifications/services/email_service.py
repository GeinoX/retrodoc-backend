from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class EmailService:

    @staticmethod
    def send_verification_email(
        user,
        verification_url,
    ):
        subject = "Verify your Retrodoc account"

        context = {
            "user": user,
            "verification_url": verification_url,
        }

        html_content = render_to_string(
            "emails/verify_email.html",
            context,
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body="Please verify your Retrodoc account.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )

        email.attach_alternative(
            html_content,
            "text/html",
        )

        email.send()