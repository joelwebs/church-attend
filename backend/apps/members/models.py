import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Member(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    membership_number = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    other_names = models.CharField(
        max_length=150,
        blank=True,
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
    )

    email = models.EmailField(blank=True)

    date_joined = models.DateField(
        default=timezone.localdate,
    )

    is_active = models.BooleanField(default=True)

    # Audit information
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members_created",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members_updated",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(
                fields=["last_name", "first_name"],
                name="member_name_idx",
            ),
            models.Index(
                fields=["is_active"],
                name="member_active_idx",
            ),
        ]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return " ".join(
            part for part in [
                self.first_name,
                self.other_names,
                self.last_name,
            ]
            if part
        )
