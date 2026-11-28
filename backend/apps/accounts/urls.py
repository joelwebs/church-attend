from django.urls import path
from .views import (
    csrf_token,
    StaffLoginView,
    CurrentStaffView,
    StaffLogoutView,
)

urlpatterns = [
    path("csrf/", csrf_token, name="csrf-token"),
    path("login/", StaffLoginView.as_view(), name="staff-login"),
    path("me/", CurrentStaffView.as_view(), name="current-staff"),
    path("logout/", StaffLogoutView.as_view(), name="staff-logout"),
]