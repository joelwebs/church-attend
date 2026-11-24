from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Member
from .permissions import IsChurchStaff
from .serializers import MemberSerializer


class MemberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class MemberViewSet(viewsets.ModelViewSet):
    serializer_class = MemberSerializer
    permission_classes = [IsChurchStaff]
    pagination_class = MemberPagination

    http_method_names = [
        "get",
        "post",
        "put",
        "patch",
        "head",
        "options",
    ]

    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "membership_number",
        "first_name",
        "last_name",
        "other_names",
        "phone_number",
        "email",
    ]

    ordering_fields = [
        "first_name",
        "last_name",
        "date_joined",
        "created_at",
    ]

    ordering = ["last_name", "first_name"]

    def get_queryset(self):
        queryset = Member.objects.all()

        active_filter = self.request.query_params.get("is_active")

        if active_filter is not None:
            if active_filter.lower() == "true":
                queryset = queryset.filter(is_active=True)
            elif active_filter.lower() == "false":
                queryset = queryset.filter(is_active=False)
            else:
                raise ValidationError({
                    "is_active": "Use true or false."
                })

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        member = self.get_object()

        if member.is_active:
            member.is_active = False
            member.updated_by = request.user
            member.save(
                update_fields=[
                    "is_active",
                    "updated_by",
                    "updated_at",
                ]
            )

        return Response(
            {
                "message": "Member deactivated successfully."
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        member = self.get_object()

        if not member.is_active:
            member.is_active = True
            member.updated_by = request.user
            member.save(
                update_fields=[
                    "is_active",
                    "updated_by",
                    "updated_at",
                ]
            )

        return Response(
            {
                "message": "Member activated successfully."
            },
            status=status.HTTP_200_OK,
        )
