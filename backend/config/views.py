
from django.db import DatabaseError, connection

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Check whether the ChurchAttend API and database are available.
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return Response(
            {
                "status": "healthy",
                "database": "connected",
                "service": "ChurchAttend API",
            },
            status=status.HTTP_200_OK,
        )

    except DatabaseError:
        return Response(
            {
                "status": "unhealthy",
                "database": "disconnected",
                "service": "ChurchAttend API",
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
