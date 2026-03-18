from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.MEMBER)
        extra_fields.setdefault("password_state", User.PasswordState.ACTIVE)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        MEMBER = "member", "Member"
        ADMIN = "admin", "Admin"

    class PasswordState(models.TextChoices):
        TEMPORARY = "temporary", "Temporary"
        ACTIVE = "active", "Active"
        RESET_REQUIRED = "reset_required", "Reset required"

    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    is_responsable_accredited = models.BooleanField(default=False)
    responsable_accredited_at = models.DateTimeField(null=True, blank=True)
    responsable_accredited_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="granted_responsable_accreditations",
    )
    has_orange_passport = models.BooleanField(default=False)
    orange_passport_granted_at = models.DateTimeField(null=True, blank=True)
    orange_passport_granted_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="granted_orange_passports",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    password_state = models.CharField(
        max_length=20,
        choices=PasswordState.choices,
        default=PasswordState.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    def save(self, *args, **kwargs):
        self.is_staff = self.role == self.Role.ADMIN or self.is_superuser
        super().save(*args, **kwargs)

    @property
    def is_admin_role(self) -> bool:
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def can_cover_slots(self) -> bool:
        return self.is_active and (self.is_admin_role or self.is_responsable_accredited)

    @property
    def can_book_free_practice(self) -> bool:
        return self.is_active and (
            self.is_admin_role or self.is_responsable_accredited or self.has_orange_passport
        )

    def grant_responsable_accreditation(self, *, actor=None):
        self.is_responsable_accredited = True
        self.responsable_accredited_at = timezone.now()
        self.responsable_accredited_by = actor

    def revoke_responsable_accreditation(self):
        self.is_responsable_accredited = False

    def grant_orange_passport(self, *, actor=None):
        self.has_orange_passport = True
        self.orange_passport_granted_at = timezone.now()
        self.orange_passport_granted_by = actor

    def revoke_orange_passport(self):
        self.has_orange_passport = False

    def set_temporary_password(self, raw_password: str, *, state: str | None = None):
        self.set_password(raw_password)
        self.password_state = state or self.PasswordState.TEMPORARY

    def mark_password_active(self):
        self.password_state = self.PasswordState.ACTIVE

    def __str__(self) -> str:
        return self.full_name or self.email
