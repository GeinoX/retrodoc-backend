from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _

# Create your models here.
class CustomUserManager(BaseUserManager):
    # def _validate_required_fields(self, **fields: str) -> None:
    #     for field_name, value in fields.items():
    #         if not value:
    #             raise ValueError(_(f"{field_name.replace('_', ' ').title()} is required."))

    def create_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        password: str,
        role: str,
        **extra_fields,
    ) -> "CustomUser":
        

        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=self.normalize_email(email) if email else None,
            role=role,
            phone=phone,
            **extra_fields,
        )  
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name: str, last_name: str, email: str, phone: str, password: str, **extra_fields) -> "CustomUser":
        extra_fields.update({"is_active": True, "is_staff": True, "is_superuser": True})
        return self.create_user(first_name, last_name, email, phone, password, role = CustomUser.RoleChoices.ADMIN, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):

    class RoleChoices(models.TextChoices):
        CITIZEN = "C", _("Citizen")
        OFFICER = "O", _("Officer")
        ADMIN = "A", _("ADMIN")

    
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(_("First Name"), max_length=50)
    last_name = models.CharField(_("Last Name"), max_length=50)
    email = models.EmailField(_("Personal Email"), max_length=254, unique=True)
    phone = models.CharField(_("Phone"), max_length=20)
    role = models.CharField(_("Role"), max_length=1, choices=RoleChoices, default=RoleChoices.CITIZEN)
 
    must_change_password = models.BooleanField(default=False)
    is_active = models.BooleanField(_("Active"), default=True)
    is_staff = models.BooleanField(_("Staff Status"), default=False)
    date_joined = models.DateTimeField(_("Date Joined"), auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return self.get_full_name()

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self) -> str:
        return self.first_name
