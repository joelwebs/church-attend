import uuid
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Service, ServiceQRToken

User = get_user_model()


class ServiceAPITests(APITestCase):

    def setUp(self):
        self.pastor = User.objects.create_user(
            username="pastor",
            password="TestPassword123!",
            role="pastor",
        )

        self.media_user = User.objects.create_user(
            username="media",
            password="TestPassword123!",
            role="media_team",
        )

        self.member_user = User.objects.create_user(
            username="unauthorized",
            password="TestPassword123!",
            role="member",
        )

        now = timezone.localtime()

        self.service_date = now.date()

        self.service = Service.objects.create(
            name="Sunday Main Service",
            date=self.service_date,
            start_time=(now + timedelta(hours=1)).time(),
            end_time=(now + timedelta(hours=3)).time(),
            venue="Main Auditorium",
            attendance_start=now - timedelta(minutes=10),
            attendance_end=now + timedelta(hours=3),
            status=Service.Status.OPEN,
            created_by=self.pastor,
        )

        self.list_url = reverse("service-list")

    def test_unauthenticated_user_cannot_list_services(self):
        response = self.client.get(self.list_url)

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_pastor_can_list_services(self):
        self.client.force_authenticate(user=self.pastor)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_media_team_can_list_services(self):
        self.client.force_authenticate(user=self.media_user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_staff_role_cannot_manage_services(self):
        self.client.force_authenticate(user=self.member_user)

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_staff_can_create_service(self):
        self.client.force_authenticate(user=self.pastor)

        now = timezone.localtime()
        service_date = (now + timedelta(days=7)).date()

        data = {
            "name": "Next Sunday Service",
            "date": service_date.isoformat(),
            "start_time": "09:00:00",
            "end_time": "11:00:00",
            "venue": "Main Auditorium",
            "attendance_start": timezone.make_aware(
                timezone.datetime.combine(
                    service_date,
                    timezone.datetime.strptime("08:00", "%H:%M").time(),
                )
            ).isoformat(),
            "attendance_end": timezone.make_aware(
                timezone.datetime.combine(
                    service_date,
                    timezone.datetime.strptime("11:30", "%H:%M").time(),
                )
            ).isoformat(),
        }

        response = self.client.post(
            self.list_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        service = Service.objects.get(name="Next Sunday Service")

        self.assertEqual(service.created_by, self.pastor)
        self.assertIsInstance(service.id, uuid.UUID)

    def test_service_uses_uuid_primary_key(self):
        self.assertIsInstance(self.service.id, uuid.UUID)

    def test_staff_can_open_service(self):
        self.client.force_authenticate(user=self.pastor)

        self.service.status = Service.Status.SCHEDULED
        self.service.save()

        response = self.client.post(
            reverse("service-open", kwargs={"pk": self.service.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.service.refresh_from_db()

        self.assertEqual(self.service.status, Service.Status.OPEN)

    def test_cancelled_service_cannot_be_opened(self):
        self.client.force_authenticate(user=self.pastor)

        self.service.status = Service.Status.CANCELLED
        self.service.save()

        response = self.client.post(
            reverse("service-open", kwargs={"pk": self.service.pk})
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_staff_can_close_service(self):
        self.client.force_authenticate(user=self.pastor)

        response = self.client.post(
            reverse("service-close", kwargs={"pk": self.service.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.service.refresh_from_db()

        self.assertEqual(self.service.status, Service.Status.CLOSED)

    def test_closing_service_revokes_active_qr_tokens(self):
        self.client.force_authenticate(user=self.pastor)

        token = ServiceQRToken.objects.create(
            service=self.service,
            token_hash=ServiceQRToken.hash_token("test-token"),
            expires_at=timezone.now() + timedelta(hours=1),
            created_by=self.pastor,
        )

        self.client.post(
            reverse("service-close", kwargs={"pk": self.service.pk})
        )

        token.refresh_from_db()

        self.assertFalse(token.is_active)

    def test_staff_can_cancel_service(self):
        self.client.force_authenticate(user=self.pastor)

        response = self.client.post(
            reverse("service-cancel", kwargs={"pk": self.service.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.service.refresh_from_db()

        self.assertEqual(
            self.service.status,
            Service.Status.CANCELLED,
        )

    @patch("apps.services.views.qrcode.make")
    def test_staff_can_generate_qr_code(self, mock_qr):
        self.client.force_authenticate(user=self.pastor)

        mock_qr.return_value.save = lambda buffer, format: buffer.write(
            b"fake-qr-image"
        )

        response = self.client.post(
            reverse("service-generate-qr", kwargs={"pk": self.service.pk})
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertIn("qr_code", response.data)
        self.assertIn("qr_token_id", response.data)

        token = ServiceQRToken.objects.get(service=self.service)

        self.assertTrue(token.is_active)
        self.assertNotIn("test-token", token.token_hash)

    def test_qr_generation_requires_open_service(self):
        self.client.force_authenticate(user=self.pastor)

        self.service.status = Service.Status.SCHEDULED
        self.service.save()

        response = self.client.post(
            reverse("service-generate-qr", kwargs={"pk": self.service.pk})
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_qr_token_is_hashed(self):
        raw_token = ServiceQRToken.generate_token()

        token_hash = ServiceQRToken.hash_token(raw_token)

        self.assertNotEqual(raw_token, token_hash)
        self.assertEqual(len(token_hash), 64)

    def test_valid_qr_token_can_be_validated(self):
        raw_token = "valid-test-token"

        ServiceQRToken.objects.create(
            service=self.service,
            token_hash=ServiceQRToken.hash_token(raw_token),
            expires_at=timezone.now() + timedelta(hours=1),
            created_by=self.pastor,
        )

        response = self.client.get(
            reverse("service-qr-validate"),
            {"token": raw_token},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["valid"])

    def test_invalid_qr_token_is_rejected(self):
        response = self.client.get(
            reverse("service-qr-validate"),
            {"token": "invalid-token"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_expired_qr_token_is_rejected(self):
        raw_token = "expired-token"

        ServiceQRToken.objects.create(
            service=self.service,
            token_hash=ServiceQRToken.hash_token(raw_token),
            expires_at=timezone.now() - timedelta(minutes=5),
            created_by=self.pastor,
        )

        response = self.client.get(
            reverse("service-qr-validate"),
            {"token": raw_token},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(response.data["valid"])

    def test_inactive_qr_token_is_rejected(self):
        raw_token = "inactive-token"

        ServiceQRToken.objects.create(
            service=self.service,
            token_hash=ServiceQRToken.hash_token(raw_token),
            expires_at=timezone.now() + timedelta(hours=1),
            is_active=False,
            created_by=self.pastor,
        )

        response = self.client.get(
            reverse("service-qr-validate"),
            {"token": raw_token},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_qr_token_requires_open_service(self):
        raw_token = "closed-service-token"

        self.service.status = Service.Status.CLOSED
        self.service.save()

        ServiceQRToken.objects.create(
            service=self.service,
            token_hash=ServiceQRToken.hash_token(raw_token),
            expires_at=timezone.now() + timedelta(hours=1),
            created_by=self.pastor,
        )

        response = self.client.get(
            reverse("service-qr-validate"),
            {"token": raw_token},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_service_date_filter(self):
        self.client.force_authenticate(user=self.pastor)

        response = self.client.get(
            self.list_url,
            {"date": self.service_date.isoformat()},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
