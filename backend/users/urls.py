from rest_framework.routers import DefaultRouter
from django.urls import include, path

from .views import (
    UsersViewSet,
    ListSubscriptions,
    FollowViewSet,
)

v1_router = DefaultRouter()

v1_router.register(
    'users',
    UsersViewSet,
    basename='Пользователи'
)

urlpatterns = [
    path(
        'users/subscriptions/',
        ListSubscriptions.as_view(),
        name="Мои подписки",
    ),
    path(
        'users/<user_id>/subscribe/',
        FollowViewSet.as_view(),
        name="Подписка",
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(v1_router.urls)),
]
