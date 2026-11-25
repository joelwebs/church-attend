
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PublicServiceQRViewSet, ServiceViewSet

router = DefaultRouter()
router.register("services", ServiceViewSet, basename="service")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "services/qr/validate/",
        PublicServiceQRViewSet.as_view({"get": "retrieve"}),
        name="service-qr-validate",
    ),
]
