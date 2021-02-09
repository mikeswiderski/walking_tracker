from datetime import date

from django.db.models import Avg
from rest_framework import generics, mixins, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.records.models import Record
from apps.records.serializers import AdminRecordSerializer, RecordSerializer
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
        return self.list(request, *args, **kwargs)

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

    def get(self, request):

        user = self.request.user
        queryset = Record.objects.filter(owner_id=user.id)

        today = date.today()

        year = request.GET.get('year', today.year)
        month = request.GET.get('month', today.month)

        def validate_arg(value):
            if type(value) == int and value is not None:
                value = int(value)
                return value
            elif value.isnumeric() and value is not None:
                value = int(value)
                return value

        year = validate_arg(year)
        month = validate_arg(month)

        if year and month:
            queryset = queryset.filter(created__year=year, created__month=month)
            average_distance = (queryset.aggregate(Avg('distance'))).get('distance__avg')
            if average_distance is not None:
                return Response({'average_distance':  average_distance}, status=status.HTTP_200_OK)
            else:
                return Response({"average_distance": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"average_distance": "Not found."}, status=status.HTTP_404_NOT_FOUND)
