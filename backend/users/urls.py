from rest_framework.routers import DefaultRouter
from django.urls import include, path
from djoser import views

from .views import (
    TokenCreateCheckBlock,
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
        'token/login/',
        TokenCreateCheckBlock.as_view(),
        name="Получить токен",
    ),
    path(
        'token/logout/',
        views.TokenDestroyView.as_view(),
        name="Удалить токен"
    ),
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
    path('', include(v1_router.urls)),
]
