from django.contrib.auth.models import AbstractUser
from django.db import models


class StaffUser(AbstractUser):
    """
    Custom user model for ChurchAttend staff.

    Members do not need accounts.
    Only Pastor and Media Team staff use this model.
    """

    ROLE_CHOICES = [
        ("pastor", "Pastor"),
        ("media_team", "Media Team"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="media_team",
    )

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
