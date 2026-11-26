
import hashlib
from datetime import time, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from apps.church.models import ChurchConfiguration
from apps.members.models import Member
from apps.services.models import Service, ServiceQRToken

from .models import Attendance


User = get_user_model()


class AttendanceAPITests(APITestCase):

    def setUp(self):
        self.pastor = User.objects.create_user(
            username="pastor",
            password="TestPassword123!",
            role="pastor",
        )

        self.member = Member.objects.create(
            first_name="John",
            last_name="Mensah",
            phone_number="0240000000",
        )

        now = timezone.now()

        self.service = Service.objects.create(
            name="Sunday Service",
            date=timezone.localdate(now),
            start_time=time(8, 0),
            end_time=time(20, 0),
            status="open",
            attendance_start=now - timedelta(minutes=30),
            attendance_end=now + timedelta(minutes=30),
        )

        self.raw_token = "test-service-qr-token"

        self.qr_token = ServiceQRToken.objects.create(
            service=self.service,
            token_hash=hashlib.sha256(
                self.raw_token.encode("utf-8")
            ).hexdigest(),
            expires_at=now + timedelta(hours=1),
            is_active=True,
        )

        ChurchConfiguration.objects.create(
            name="Grace Church",
            address="Accra, Ghana",
            latitude="5.603717",
            longitude="-0.186964",
            check_in_radius_meters=100,
            max_gps_accuracy_meters=50,
            is_active=True,
        )

        self.check_in_url = reverse("self-check-in")

        self.check_in_data = {
            "token": self.raw_token,
            "member_id": self.member.pk,
            "latitude": "5.603717",
            "longitude": "-0.186964",
            "accuracy_meters": "10.00",
        }

    def test_member_can_check_in_successfully(self):
        response = self.client.post(
            self.check_in_url,
            self.check_in_data,
            format="json",
        )

        print(
            "\nSELF CHECK-IN RESPONSE:",
            response.status_code,
            response.data,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(Attendance.objects.count(), 1)

        attendance = Attendance.objects.first()

        self.assertEqual(attendance.member, self.member)
        self.assertEqual(attendance.service, self.service)
        self.assertEqual(attendance.check_in_method, "self")
        self.assertTrue(attendance.gps_verified)

    def test_duplicate_check_in_is_rejected(self):
        self.client.post(
            self.check_in_url,
            self.check_in_data,
            format="json",
        )

        response = self.client.post(
            self.check_in_url,
            self.check_in_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(Attendance.objects.count(), 1)

    def test_invalid_qr_token_is_rejected(self):
        data = self.check_in_data.copy()
        data["token"] = "invalid-token"

        response = self.client.post(
            self.check_in_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(Attendance.objects.count(), 0)

    def test_poor_gps_accuracy_is_rejected(self):
        data = self.check_in_data.copy()
        data["accuracy_meters"] = "100.00"

        response = self.client.post(
            self.check_in_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(Attendance.objects.count(), 0)

    def test_outside_church_radius_is_rejected(self):
        data = self.check_in_data.copy()

        data["latitude"] = "5.610000"
        data["longitude"] = "-0.186964"

        response = self.client.post(
            self.check_in_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(Attendance.objects.count(), 0)

    def test_staff_can_view_attendance_records(self):
        self.client.force_authenticate(user=self.pastor)

        response = self.client.get(
            reverse("attendance-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_unauthenticated_user_cannot_view_attendance_records(self):
        response = self.client.get(
            reverse("attendance-list")
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_staff_can_record_assisted_attendance(self):
        self.client.force_authenticate(user=self.pastor)

        response = self.client.post(
            reverse("assisted-check-in"),
            {
                "member_id": self.member.pk,
                "service_id": str(self.service.pk),
            },
            format="json",
        )

        print(
            "\nASSISTED CHECK-IN RESPONSE:",
            response.status_code,
            response.data,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        attendance = Attendance.objects.get(
            member=self.member,
            service=self.service,
        )

        self.assertEqual(attendance.check_in_method, "assisted")
        self.assertEqual(attendance.recorded_by, self.pastor)
        self.assertFalse(attendance.gps_verified)
