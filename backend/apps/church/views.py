from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import ChurchConfiguration
from .permissions import IsChurchStaff
from .serializers import ChurchConfigurationSerializer


class ChurchConfigurationViewSet(viewsets.ModelViewSet):
    serializer_class = ChurchConfigurationSerializer
    permission_classes = [IsChurchStaff]

    http_method_names = ["get", "post", "put", "patch", "head", "options"]

    def get_queryset(self):
        return ChurchConfiguration.objects.all()[:1]

    def create(self, request, *args, **kwargs):
        if ChurchConfiguration.objects.exists():
            raise ValidationError(
                {"detail": "Church configuration already exists."}
            )

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "Church configuration cannot be deleted."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
