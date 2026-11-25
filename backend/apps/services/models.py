import hashlib
import secrets
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Service(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(max_length=150)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=200, blank=True)

    attendance_start = models.DateTimeField()
    attendance_end = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
        db_index=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="services_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-start_time"]
        indexes = [
            models.Index(fields=["date", "status"], name="service_date_status_idx"),
        ]

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError({
                "end_time": "End time must be after start time."
            })

        if self.attendance_end <= self.attendance_start:
            raise ValidationError({
                "attendance_end": "Attendance end must be after attendance start."
            })

        if timezone.is_aware(self.attendance_start):
            if timezone.localtime(self.attendance_start).date() != self.date:
                raise ValidationError({
                    "attendance_start": "Attendance must start on the service date."
                })

        if timezone.is_aware(self.attendance_end):
            if timezone.localtime(self.attendance_end).date() != self.date:
                raise ValidationError({
                    "attendance_end": "Attendance must end on the service date."
                })

    def __str__(self):
        return f"{self.name} - {self.date}"


class ServiceQRToken(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="qr_tokens",
    )

    token_hash = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
    )

    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @staticmethod
    def hash_token(raw_token):
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    @classmethod
    def generate_token(cls):
        return secrets.token_urlsafe(32)

    def is_valid(self):
        return (
            self.is_active
            and self.service.status == Service.Status.OPEN
            and timezone.now() <= self.expires_at
            and timezone.now() >= self.service.attendance_start
            and timezone.now() <= self.service.attendance_end
        )

    def __str__(self):
        return f"QR token for {self.service}"
