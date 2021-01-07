from django.urls import path
from apps.records import views

urlpatterns = [
    path('', views.RecordList.as_view(), name='record-create-list'),
    path(
        '<int:pk>/',
        views.RecordDetail.as_view(),
        name='record-detail-update-delete',
    ),
]
