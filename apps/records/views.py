from datetime import date

from django.core.exceptions import FieldError, ValidationError
from django.db.models import Avg
from rest_framework import generics, mixins, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.records.models import Record
from apps.records.serializers import AdminRecordSerializer, RecordSerializer
from apps.records.utils import parse_search
from apps.users.models import User


class RecordList(mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 generics.GenericAPIView):
    permission_classes = (IsAuthenticated, )

    def get_serializer_class(self):
        if self.request.user.role == User.MEMBER:
            return RecordSerializer
        elif self.request.user.role == User.MANAGER:
            return RecordSerializer
        elif self.request.user.role == User.ADMIN:
            return AdminRecordSerializer

    def get_queryset(self):
        queryset = Record.objects.all()
        user = self.request.user
        if user.role == User.MEMBER:
            queryset = queryset.filter(owner_id=user.id)
        elif user.role == User.MANAGER:
            queryset = queryset.filter(owner_id=user.id)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == User.ADMIN:
            serializer.save()
        else:
            serializer.save(owner=self.request.user)

    def get(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        search = request.GET.get('search')

        if search is not None:
            try:
                result = parse_search(search)
            except ValidationError:
                return Response(
                    {"detail": "Bad search phrase, try again."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                queryset = queryset.filter(result)
            except (ValueError, FieldError):
                return Response(
                    {"detail": "Bad Value(s) for field(s) or bad field name(s)"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RecordDetail(mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   generics.GenericAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = RecordSerializer

    def get_queryset(self):
        queryset = Record.objects.all()
        user = self.request.user
        if user.role == User.MEMBER or user.role == User.MANAGER:
            queryset = queryset.filter(owner_id=user.id)
        return queryset

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class AverageDistance(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):

        try:
            User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        queryset = Record.objects.all()
        user = self.request.user

        if user.role != User.ADMIN and user.id != user_id:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        queryset = queryset.filter(owner_id=user_id)

        today = date.today()

        year = request.GET.get('year')
        month = request.GET.get('month')

        if year is None and month is None:
            year = today.year
            month = today.month

        if year is None:
            return Response({"detail": "Must provide year and month"}, status=status.HTTP_400_BAD_REQUEST)

        if month is None:
            return Response({"detail": "Must provide year and month"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except ValueError:
            return Response({"detail": "year must be integer"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            month = int(month)
        except ValueError:
            return Response({"detail": "month must be integer"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = queryset.filter(created__year=year, created__month=month)
        average_distance = (queryset.aggregate(Avg('distance'))).get('distance__avg')
        return Response({'average_distance':  average_distance}, status=status.HTTP_200_OK)
