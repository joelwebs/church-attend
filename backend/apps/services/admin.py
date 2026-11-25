from django.contrib import admin
from .models import Service, ServiceQRToken

class ServiceQRTokenInline(admin.TabularInline):
    model = ServiceQRToken
    extra = 0
    readonly_fields = (
        "id",
        "token_hash",
        "created_at",
        "created_by",
    )
    fields = (
        "id",
        "expires_at",
        "is_active",
        "token_hash",
        "created_at",
    )
    can_delete = False


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "date",
        "start_time",
        "end_time",
        "status",
        "venue",
    )
    list_filter = ("status", "date")
    search_fields = ("name", "venue")
    readonly_fields = ("id", "created_at", "updated_at")
    inlines = [ServiceQRTokenInline]


@admin.register(ServiceQRToken)
class ServiceQRTokenAdmin(admin.ModelAdmin):
    list_display = (
        "service",
        "expires_at",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active",)
    readonly_fields = (
        "id",
        "token_hash",
        "created_at",
        "created_by",
    )
