from rest_framework.permissions import BasePermission

class IsChurchStaff(BasePermission):
    message = "You are not authorized to manage services."

    allowed_roles = {"pastor", "media_team"}

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and getattr(user, "role", None) in self.allowed_roles
        )