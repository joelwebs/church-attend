
from decimal import Decimal

from rest_framework import serializers

from .models import Attendance


class SelfCheckInSerializer(serializers.Serializer):
    token = serializers.CharField(
        max_length=200,
        trim_whitespace=True,
    )

    member_id = serializers.UUIDField()

    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=Decimal("-90"),
        max_value=Decimal("90"),
    )

    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=Decimal("-180"),
        max_value=Decimal("180"),
    )

    accuracy_meters = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )


class AssistedCheckInSerializer(serializers.Serializer):
    member_id = serializers.UUIDField()
    service_id = serializers.UUIDField()



class AttendanceSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(
        source="member.full_name",
        read_only=True,
    )

    service_name = serializers.CharField(
        source="service.name",
        read_only=True,
    )

    class Meta:
        model = Attendance
        fields = [
            "id",
            "member",
            "member_name",
            "service",
            "service_name",
            "check_in_method",
            "recorded_by",
            "check_in_time",
            "gps_verified",
            "latitude",
            "longitude",
            "created_at",
        ]
        read_only_fields = fields
