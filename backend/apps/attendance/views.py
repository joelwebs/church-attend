
from django.db import IntegrityError, transaction
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.members.models import Member
from apps.services.models import Service

from .models import Attendance
from .permissions import IsChurchStaff
from .serializers import (
    AttendanceSerializer,
    AssistedCheckInSerializer,
    SelfCheckInSerializer,
)
from .utils import (
    validate_service_qr,
    verify_church_location,
)


def check_service_is_open(service):
    now = timezone.now()

    if service.status != "open":
        raise ValidationError(
            {"service": "This service is not open."}
        )

    if (
        service.attendance_start is None
        or service.attendance_end is None
        or not service.attendance_start <= now <= service.attendance_end
    ):
        raise ValidationError(
            {"service": "Attendance is currently closed."}
        )


def save_attendance(**kwargs):
    try:
        with transaction.atomic():
            return Attendance.objects.create(**kwargs)
    except IntegrityError:
        raise ValidationError(
            {"attendance": "This member has already checked in for this service."}
        )


class PublicMemberSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get("token")
        query = request.query_params.get("q", "").strip()

        validate_service_qr(token)

        if len(query) < 2:
            raise ValidationError(
                {"q": "Enter at least two characters to search."}
            )

        from django.db.models import Q

        members = (
            Member.objects
            .filter(is_active=True)
            .filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(other_names__icontains=query)
            )
            .order_by("last_name", "first_name")[:10]
        )

        results = [
            {
                "id": member.pk,
                "full_name": member.full_name,
            }
            for member in members
        ]

        return Response(results, status=status.HTTP_200_OK)


class SelfCheckInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SelfCheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        qr_token = validate_service_qr(data["token"])

        try:
            member = Member.objects.get(
                pk=data["member_id"],
                is_active=True,
            )
        except Member.DoesNotExist:
            raise NotFound("Member not found or inactive.")

        verify_church_location(
            latitude=data["latitude"],
            longitude=data["longitude"],
            accuracy=data["accuracy_meters"],
        )

        attendance = save_attendance(
            member=member,
            service=qr_token.service,
            check_in_method="self",
            recorded_by=None,
            gps_verified=True,
            latitude=data["latitude"],
            longitude=data["longitude"],
            gps_accuracy_meters=data["accuracy_meters"],
        )

        return Response(
            {
                "message": "Attendance recorded successfully.",
                "attendance": AttendanceSerializer(attendance).data,
            },
            status=status.HTTP_201_CREATED,
        )


class AssistedCheckInView(APIView):
    permission_classes = [IsChurchStaff]

    def post(self, request):
        serializer = AssistedCheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            member = Member.objects.get(
                pk=data["member_id"],
                is_active=True,
            )
        except Member.DoesNotExist:
            raise NotFound("Member not found or inactive.")

        try:
            service = Service.objects.get(pk=data["service_id"])
        except Service.DoesNotExist:
            raise NotFound("Service not found.")

        check_service_is_open(service)

        attendance = save_attendance(
            member=member,
            service=service,
            check_in_method="assisted",
            recorded_by=request.user,
            gps_verified=False,
        )

        return Response(
            {
                "message": "Assisted attendance recorded successfully.",
                "attendance": AttendanceSerializer(attendance).data,
            },
            status=status.HTTP_201_CREATED,
        )


class AttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsChurchStaff]

    queryset = Attendance.objects.select_related(
        "member",
        "service",
        "recorded_by",
    ).all()

    def get_queryset(self):
        queryset = super().get_queryset()

        service_id = self.request.query_params.get("service")
        member_id = self.request.query_params.get("member")

        if service_id:
            queryset = queryset.filter(service_id=service_id)

        if member_id:
            queryset = queryset.filter(member_id=member_id)

        return queryset
