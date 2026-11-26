from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AttendanceViewSet,
    AssistedCheckInView,
    PublicMemberSearchView,
    SelfCheckInView,
)


router = DefaultRouter()

router.register(
    "attendance",
    AttendanceViewSet,
    basename="attendance",
)


urlpatterns = [
    path(
        "check-in/members/",
        PublicMemberSearchView.as_view(),
        name="public-member-search",
    ),
    path(
        "check-in/",
        SelfCheckInView.as_view(),
        name="self-check-in",
    ),
    path(
        "attendance/assisted/",
        AssistedCheckInView.as_view(),
        name="assisted-check-in",
    ),
    path("", include(router.urls)),
]
