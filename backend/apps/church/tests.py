from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import ChurchConfiguration


User = get_user_model()


class ChurchConfigurationAPITests(APITestCase):

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

        self.list_url = reverse("church-configuration-list")

    def test_unauthenticated_user_cannot_access_configuration(self):
        response = self.client.get(self.list_url)

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_pastor_can_create_configuration(self):
        self.client.force_authenticate(user=self.pastor)

        response = self.client.post(
            self.list_url,
            {
                "name": "Grace Church",
                "address": "Accra, Ghana",
                "latitude": "5.603717",
                "longitude": "-0.186964",
                "check_in_radius_meters": 100,
                "max_gps_accuracy_meters": 50,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ChurchConfiguration.objects.count(), 1)

    def test_media_team_can_view_configuration(self):
        ChurchConfiguration.objects.create(
            name="Grace Church",
            latitude="5.603717",
            longitude="-0.186964",
        )

        self.client.force_authenticate(user=self.media_user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_duplicate_configuration_is_rejected(self):
        ChurchConfiguration.objects.create(
            name="Grace Church",
            latitude="5.603717",
            longitude="-0.186964",
        )

        self.client.force_authenticate(user=self.pastor)

        response = self.client.post(
            self.list_url,
            {
                "name": "Another Church",
                "latitude": "5.600000",
                "longitude": "-0.180000",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_invalid_latitude_is_rejected(self):
        self.client.force_authenticate(user=self.pastor)

        response = self.client.post(
            self.list_url,
            {
                "name": "Grace Church",
                "latitude": "100",
                "longitude": "-0.186964",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
