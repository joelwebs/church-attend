
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


class HealthCheckTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_health_check_returns_200(self):
        response = self.client.get(reverse("health-check"))

        self.assertEqual(response.status_code, 200)

    def test_health_check_returns_healthy_status(self):
        response = self.client.get(reverse("health-check"))

        self.assertEqual(response.data["status"], "healthy")

    def test_health_check_confirms_database_connection(self):
        response = self.client.get(reverse("health-check"))

        self.assertEqual(response.data["database"], "connected")

    def test_health_check_returns_service_name(self):
        response = self.client.get(reverse("health-check"))

        self.assertEqual(
            response.data["service"],
            "ChurchAttend API",
        )
