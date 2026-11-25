from rest_framework import serializers
from .models import Service, ServiceQRToken

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "date",
            "start_time",
            "end_time",
            "venue",
            "attendance_start",
            "attendance_end",
            "status",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "created_by",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        start_time = attrs.get(
            "start_time",
            getattr(self.instance, "start_time", None),
        )
        end_time = attrs.get(
            "end_time",
            getattr(self.instance, "end_time", None),
        )
        attendance_start = attrs.get(
            "attendance_start",
            getattr(self.instance, "attendance_start", None),
        )
        attendance_end = attrs.get(
            "attendance_end",
            getattr(self.instance, "attendance_end", None),
        )
        date = attrs.get(
            "date",
            getattr(self.instance, "date", None),
        )

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({
                "end_time": "End time must be after start time."
            })

        if attendance_start and attendance_end:
            if attendance_end <= attendance_start:
                raise serializers.ValidationError({
                    "attendance_end": "Attendance end must be after attendance start."
                })

        if date and attendance_start and attendance_end:
            if attendance_start.date() != date or attendance_end.date() != date:
                raise serializers.ValidationError(
                    "Attendance window must fall on the service date."
                )

        return attrs


class ServiceQRTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceQRToken
        fields = [
            "id",
            "service",
            "expires_at",
            "is_active",
            "created_at",
        ]
        read_only_fields = fields
