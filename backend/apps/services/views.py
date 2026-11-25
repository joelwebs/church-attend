import base64
from io import BytesIO

import qrcode

from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Service, ServiceQRToken
from .permissions import IsChurchStaff
from .serializers import ServiceSerializer


class ServicePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [IsChurchStaff]
    pagination_class = ServicePagination

    http_method_names = [
        "get", "post", "put", "patch", "head", "options"
    ]

    def get_queryset(self):
        queryset = Service.objects.select_related("created_by")

        service_date = self.request.query_params.get("date")
        service_status = self.request.query_params.get("status")

        if service_date:
            queryset = queryset.filter(date=service_date)

        if service_status:
            queryset = queryset.filter(status=service_status)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def open(self, request, pk=None):
        service = self.get_object()

        if service.status == Service.Status.CANCELLED:
            raise ValidationError("Cancelled services cannot be opened.")

        if service.status == Service.Status.CLOSED:
            raise ValidationError("Closed services cannot be reopened.")

        service.status = Service.Status.OPEN
        service.save(update_fields=["status", "updated_at"])

        return Response(
            {"message": "Service opened successfully."}
        )

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        service = self.get_object()

        service.status = Service.Status.CLOSED
        service.save(update_fields=["status", "updated_at"])

        service.qr_tokens.filter(is_active=True).update(is_active=False)

        return Response(
            {"message": "Service closed successfully."}
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        service = self.get_object()

        service.status = Service.Status.CANCELLED
        service.save(update_fields=["status", "updated_at"])

        service.qr_tokens.filter(is_active=True).update(is_active=False)

        return Response(
            {"message": "Service cancelled successfully."}
        )

    @action(detail=True, methods=["post"])
    def generate_qr(self, request, pk=None):
        service = self.get_object()

        if service.status != Service.Status.OPEN:
            raise ValidationError(
                "Open the service before generating its QR code."
            )

        now = timezone.now()

        if now < service.attendance_start or now > service.attendance_end:
            raise ValidationError(
                "The attendance window is not currently open."
            )

        # Revoke previous tokens to prevent multiple active QR codes.
        service.qr_tokens.filter(is_active=True).update(is_active=False)

        raw_token = ServiceQRToken.generate_token()

        qr_token = ServiceQRToken.objects.create(
            service=service,
            token_hash=ServiceQRToken.hash_token(raw_token),
            expires_at=service.attendance_end,
            created_by=request.user,
        )

        # The QR contains only the public check-in route and raw token.
        # Configure FRONTEND_CHECKIN_URL in Django settings.
        from django.conf import settings

        frontend_url = getattr(
            settings,
            "FRONTEND_CHECKIN_URL",
            "http://localhost:5173/check-in",
        )

        qr_url = f"{frontend_url}?token={raw_token}"

        qr = qrcode.make(qr_url)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        qr_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return Response(
            {
                "message": "QR code generated successfully.",
                "service_id": str(service.id),
                "qr_token_id": str(qr_token.id),
                "qr_code": f"data:image/png;base64,{qr_image}",
                "expires_at": qr_token.expires_at,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def revoke_qr(self, request, pk=None):
        service = self.get_object()

        updated = service.qr_tokens.filter(is_active=True).update(
            is_active=False
        )

        return Response({
            "message": "QR tokens revoked successfully.",
            "revoked_count": updated,
        })


class PublicServiceQRViewSet(viewsets.ViewSet):
    """
    Public endpoint for validating a QR token.
    Does not expose staff-only service management.
    """

    authentication_classes = []
    permission_classes = []

    def retrieve(self, request, pk=None):
        raw_token = request.query_params.get("token")

        if not raw_token:
            raise ValidationError({"token": "QR token is required."})

        token_hash = ServiceQRToken.hash_token(raw_token)

        qr_token = get_object_or_404(
            ServiceQRToken.objects.select_related("service"),
            token_hash=token_hash,
        )

        if not qr_token.is_valid():
            return Response(
                {"valid": False, "message": "This QR code is expired or invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({
            "valid": True,
            "service": {
                "id": str(qr_token.service.id),
                "name": qr_token.service.name,
                "date": qr_token.service.date,
                "venue": qr_token.service.venue,
            },
        })
