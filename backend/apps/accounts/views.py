
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication

from .serializers import StaffUserSerializer


@ensure_csrf_cookie
@require_GET
def csrf_token(request):
    return JsonResponse({"detail": "CSRF cookie set"})


class StaffLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @method_decorator(__import__(
        "django.views.decorators.csrf",
        fromlist=["csrf_protect"]
    ).csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        username = request.data.get("username", "").strip()
        password = request.data.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None or not user.is_active:
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.role not in ["pastor", "media_team"]:
            return Response(
                {"detail": "You do not have staff access."},
                status=status.HTTP_403_FORBIDDEN,
            )

        login(request, user)

        return Response(
            StaffUserSerializer(user).data,
            status=status.HTTP_200_OK,
        )


class CurrentStaffView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ["pastor", "media_team"]:
            return Response(
                {"detail": "You do not have staff access."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(StaffUserSerializer(request.user).data)


class StaffLogoutView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
