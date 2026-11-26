from rest_framework import serializers
from .models import ChurchConfiguration

class ChurchConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurchConfiguration
        fields = [
            "id",
            "name",
            "address",
            "latitude",
            "longitude",
            "check_in_radius_meters",
            "max_gps_accuracy_meters",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_latitude(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError(
                "Latitude must be between -90 and 90."
            )
        return value

    def validate_longitude(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError(
                "Longitude must be between -180 and 180."
            )
        return value
