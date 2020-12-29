from django.urls import path
from apps.users import views

urlpatterns = [
    path('', views.UserList.as_view(), name='user-create-list'),
    path(
        '<int:pk>/',
        views.UserDetail.as_view(),
        name='user-detail-update-delete',
    ),
]
