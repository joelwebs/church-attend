from django.contrib import admin
from .models import ChurchConfiguration


@admin.register(ChurchConfiguration)
class ChurchConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "latitude",
        "longitude",
        "check_in_radius_meters",
        "max_gps_accuracy_meters",
        "is_active",
    )

    readonly_fields = ("created_at", "updated_at")
