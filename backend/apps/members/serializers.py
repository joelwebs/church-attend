from rest_framework import serializers
from .models import Member

class MemberSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Member
        fields = [
            "id",
            "membership_number",
            "first_name",
            "last_name",
            "other_names",
            "full_name",
            "phone_number",
            "email",
            "date_joined",
            "is_active",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "full_name",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

        extra_kwargs = {
            "membership_number": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
        }

    def validate_first_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "First name is required."
            )

        return value

    def validate_last_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Last name is required."
            )

        return value

    def validate_membership_number(self, value):
        if value is None:
            return None

        value = value.strip().upper()

        return value or None

    def validate_phone_number(self, value):
        return value.strip()

    def validate_email(self, value):
        return value.strip().lower()
