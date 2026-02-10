from django.urls import path
from .views import hello_world
from .views import TrailList, TrailDetail

urlpatterns = [
    path('hello/', hello_world, name='hello_world'),
    path('trails/', TrailList.as_view(), name='trail-list'),
    path('trails/<int:pk>/', TrailDetail.as_view(), name='trail-detail'),
]