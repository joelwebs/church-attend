
from django.utils import timezone

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
        "delete",
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
        # Archived endpoint and restore action can access archived members.
        if self.action in ["archived", "restore"]:
            queryset = Member.objects.filter(is_deleted=True)
        else:
            queryset = Member.objects.filter(is_deleted=False)

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

    def perform_destroy(self, instance):
        # Soft delete: preserve the database record.
        instance.is_deleted = True
        instance.is_active = False
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.updated_by = self.request.user

        instance.save(
            update_fields=[
                "is_deleted",
                "is_active",
                "deleted_at",
                "deleted_by",
                "updated_by",
                "updated_at",
            ]
        )

    @action(detail=False, methods=["get"])
    def archived(self, request):
        """Return archived members."""
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        """Restore an archived member."""
        member = self.get_object()

        member.is_deleted = False
        member.deleted_at = None
        member.deleted_by = None
        member.updated_by = request.user

        # Keep the member inactive until staff explicitly activates them.
        member.is_active = False

        member.save(
            update_fields=[
                "is_deleted",
                "deleted_at",
                "deleted_by",
                "updated_by",
                "is_active",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": "Member restored successfully.",
                "member": self.get_serializer(member).data,
            },
            status=status.HTTP_200_OK,
        )

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
