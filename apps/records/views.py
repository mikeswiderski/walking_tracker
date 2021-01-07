from apps.records.models import Record
from apps.users.models import User
from apps.records.serializers import (
    RecordSerializer,
    AdminRecordSerializer,
)
from rest_framework import mixins
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class RecordList(mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 generics.GenericAPIView):
    permission_classes = (IsAuthenticated, )

    def get_serializer_class(self):
        if (self.request.user.role == User.MEMBER):
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
