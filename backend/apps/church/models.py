from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class ChurchConfiguration(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255, blank=True)

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
    )

    check_in_radius_meters = models.PositiveIntegerField(
        default=100,
        validators=[
            MinValueValidator(10),
            MaxValueValidator(1000),
        ],
    )

    max_gps_accuracy_meters = models.PositiveIntegerField(
        default=50,
        validators=[
            MinValueValidator(5),
            MaxValueValidator(200),
        ],
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Church Configuration"
        verbose_name_plural = "Church Configuration"

    def __str__(self):
        return self.name
