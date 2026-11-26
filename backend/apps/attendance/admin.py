from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "member",
        "service",
        "check_in_method",
        "check_in_time",
        "gps_verified",
        "recorded_by",
    )

    list_filter = (
        "check_in_method",
        "gps_verified",
        "check_in_time",
    )

    search_fields = (
        "member__first_name",
        "member__last_name",
        "member__membership_number",
        "service__name",
    )

    readonly_fields = (
        "member",
        "service",
        "check_in_method",
        "recorded_by",
        "check_in_time",
        "gps_verified",
        "latitude",
        "longitude",
        "gps_accuracy_meters",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
