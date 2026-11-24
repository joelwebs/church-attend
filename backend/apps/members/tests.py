from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Member


User = get_user_model()


class MemberAPITests(APITestCase):

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

        self.member = Member.objects.create(
            first_name="John",
            last_name="Mensah",
            phone_number="0240000000",
        )

        self.list_url = reverse("member-list")

    def test_unauthenticated_user_cannot_list_members(self):
        response = self.client.get(self.list_url)

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_pastor_can_list_members(self):
        self.client.force_authenticate(user=self.pastor)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_media_team_can_list_members(self):
        self.client.force_authenticate(user=self.media_user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pastor_can_create_member(self):
        self.client.force_authenticate(user=self.pastor)

        response = self.client.post(
            self.list_url,
            {
                "membership_number": "CH-001",
                "first_name": "Mary",
                "last_name": "Owusu",
                "phone_number": "0200000000",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(Member.objects.count(), 2)

        new_member = Member.objects.get(
            membership_number="CH-001"
        )

        self.assertEqual(new_member.created_by, self.pastor)

    def test_staff_can_search_members(self):
        self.client.force_authenticate(user=self.pastor)

        response = self.client.get(
            self.list_url,
            {"search": "John"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_staff_can_deactivate_member(self):
        self.client.force_authenticate(user=self.pastor)

        url = reverse(
            "member-deactivate",
            kwargs={"pk": self.member.pk},
        )

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.member.refresh_from_db()
        self.assertFalse(self.member.is_active)

    def test_staff_can_reactivate_member(self):
        self.member.is_active = False
        self.member.save()

        self.client.force_authenticate(user=self.pastor)

        url = reverse(
            "member-activate",
            kwargs={"pk": self.member.pk},
        )

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.member.refresh_from_db()
        self.assertTrue(self.member.is_active)

    def test_duplicate_membership_number_is_rejected(self):
        Member.objects.create(
            membership_number="CH-002",
            first_name="First",
            last_name="Member",
        )

        self.client.force_authenticate(user=self.pastor)

        response = self.client.post(
            self.list_url,
            {
                "membership_number": "CH-002",
                "first_name": "Second",
                "last_name": "Member",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
