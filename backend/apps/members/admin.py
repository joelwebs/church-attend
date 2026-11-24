from django.contrib import admin

from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "membership_number",
        "first_name",
        "last_name",
        "phone_number",
        "is_active",
        "date_joined",
    )

    search_fields = (
        "membership_number",
        "first_name",
        "last_name",
        "other_names",
        "phone_number",
        "email",
    )

    list_filter = (
        "is_active",
        "date_joined",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    ordering = ("last_name", "first_name")
