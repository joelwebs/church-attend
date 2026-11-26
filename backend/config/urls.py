
from django.contrib import admin
from django.urls import include, path

from config.views import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
    path("api/", include("apps.members.urls")),
    path("api/", include("apps.services.urls")),
    path("api/", include("apps.church.urls")),
]
