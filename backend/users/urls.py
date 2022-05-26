from rest_framework.routers import DefaultRouter
from django.urls import include, path

from .views import UserViewSet

v1_router = DefaultRouter()
v1_router.register(
    'users',
    UserViewSet,
    basename='Пользователи'
)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(v1_router.urls)),
]
