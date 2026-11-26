from rest_framework.routers import DefaultRouter
from .views import ChurchConfigurationViewSet

router = DefaultRouter()

router.register(
    "church",
    ChurchConfigurationViewSet,
    basename="church-configuration",
)

urlpatterns = router.urls
