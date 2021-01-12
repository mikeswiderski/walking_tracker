from apps.users.models import User
from apps.users.serializers import (
    UserMemberSerializer, UserManagerSerializer,
    UserAdminSerializer, UserMemberUpdateSerializer,
    UserManagerUpdateSerializer, UserAdminUpdateSerializer,
)
from rest_framework import mixins
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class IsAuthenticatedNotPost(IsAuthenticated):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return super(IsAuthenticatedNotPost, self).has_permission(
            request,
            view,
        )


class UserList(mixins.ListModelMixin,
               mixins.CreateModelMixin,
               generics.GenericAPIView):

    permission_classes = (IsAuthenticatedNotPost, )

    def get_queryset(self):
        queryset = User.objects.all()
        user = self.request.user
        if user.role == User.MEMBER:
            queryset = queryset.filter(id=user.id)
        return queryset

    def get_serializer_class(self):
        if (self.request.user.is_anonymous or
                self.request.user.role == User.MEMBER):
            return UserMemberSerializer
        elif self.request.user.role == User.MANAGER:
            return UserManagerSerializer
        elif self.request.user.role == User.ADMIN:
            return UserAdminSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class UserDetail(mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 generics.GenericAPIView):
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        queryset = User.objects.all()
        user = self.request.user
        if user.role == User.MEMBER:
            queryset = queryset.filter(id=user.id)
        elif user.role == User.MANAGER:
            queryset = queryset.exclude(role=User.ADMIN)
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            if self.request.user.role == User.MEMBER:
                return UserMemberUpdateSerializer
            elif self.request.user.role == User.MANAGER:
                return UserManagerUpdateSerializer
            elif self.request.user.role == User.ADMIN:
                return UserAdminUpdateSerializer
        else:
            if self.request.user.role == User.MEMBER:
                return UserMemberSerializer
            elif self.request.user.role == User.MANAGER:
                return UserManagerSerializer
            elif self.request.user.role == User.ADMIN:
                return UserAdminSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
