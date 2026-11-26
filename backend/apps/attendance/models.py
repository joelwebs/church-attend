from django.conf import settings
from django.db import models


class Attendance(models.Model):

    CHECK_IN_METHODS = [
        ("self", "Self Check-in"),
        ("assisted", "Usher Assisted"),
    ]

    member = models.ForeignKey(
        "members.Member",
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )

    service = models.ForeignKey(
        "services.Service",
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )

    check_in_method = models.CharField(
        max_length=20,
        choices=CHECK_IN_METHODS,
    )

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_records_created",
    )

    check_in_time = models.DateTimeField(auto_now_add=True)

    gps_verified = models.BooleanField(default=False)

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
    )

    gps_accuracy_meters = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-check_in_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["member", "service"],
                name="unique_member_service_attendance",
            )
        ]
        indexes = [
            models.Index(
                fields=["service", "check_in_time"],
                name="attendance_service_time_idx",
            ),
            models.Index(
                fields=["member", "check_in_time"],
                name="attendance_member_time_idx",
            ),
        ]

    def __str__(self):
        return f"{self.member} - {self.service}"
