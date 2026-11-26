
import hashlib
import math

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.services.models import ServiceQRToken
from apps.church.models import ChurchConfiguration


def calculate_distance_meters(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS coordinates using Haversine."""

    earth_radius = 6371000

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))
    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return earth_radius * c


def validate_service_qr(raw_token):
    if not raw_token:
        raise ValidationError({"token": "QR token is required."})

    token_hash = hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()

    token = (
        ServiceQRToken.objects
        .select_related("service")
        .filter(token_hash=token_hash)
        .first()
    )

    if token is None:
        raise ValidationError({"token": "Invalid QR code."})

    now = timezone.now()
    service = token.service

    if not token.is_active:
        raise ValidationError({"token": "This QR code is inactive."})

    if token.expires_at <= now:
        raise ValidationError({"token": "This QR code has expired."})

    if service.status != "open":
        raise ValidationError({"service": "This service is not open."})

    if (
        service.attendance_start is None
        or service.attendance_end is None
        or not service.attendance_start <= now <= service.attendance_end
    ):
        raise ValidationError(
            {"service": "Attendance is currently closed for this service."}
        )

    return token


def verify_church_location(latitude, longitude, accuracy):
    configuration = (
        ChurchConfiguration.objects
        .filter(is_active=True)
        .first()
    )

    if configuration is None:
        raise ValidationError(
            {"location": "Church location has not been configured."}
        )

    if accuracy > configuration.max_gps_accuracy_meters:
        raise ValidationError(
            {"accuracy": "GPS accuracy is insufficient for check-in."}
        )

    distance = calculate_distance_meters(
        configuration.latitude,
        configuration.longitude,
        latitude,
        longitude,
    )

    if distance > configuration.check_in_radius_meters:
        raise ValidationError(
            {"location": "You are outside the permitted church check-in area."}
        )

    return True
