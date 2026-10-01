from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser
from .forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
)


# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = (
        "email",
        "first_name",
        "last_name",
        "phone",
        "role",
        "is_active",
        "is_staff",
        "date_joined",
    )

    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "must_change_password",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
        "phone",
    )

    ordering = (
        "last_name",
        "first_name",
    )

    readonly_fields = (
        "date_joined",
    )

    fieldsets = (
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                )
            },
        ),
        (
            "Role & Access",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "must_change_password",
                )
            },
        ),
        (
            "Authentication",
            {
                "fields": (
                    "password",
                    "last_login",
                    "date_joined",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            "Personal Information",
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
        (
            "Access",
            {
                "classes": ("wide",),
                "fields": (
                    "is_active",
                    "is_staff",
                    "must_change_password",
                ),
            },
        ),
    )