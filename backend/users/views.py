from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from djoser.views import UserViewSet

from .models import User, Follow
from .serializers import (
    FollowSerializer,
)


class UserViewSet(UserViewSet):

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        subscriber = request.user
        queryset = Follow.objects.filter(subscriber=subscriber)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True, methods=['post'], permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        subscriber = request.user
        author = get_object_or_404(User, id=id)

        if subscriber == author:
            return Response({
                'errors': 'Нельзя подписаться на себя'
            }, status=status.HTTP_400_BAD_REQUEST)
        if subscriber.authors.filter(author=author).exists():
            return Response({
                'errors': 'Уже есть подпискa на этого пользователя'
            }, status=status.HTTP_400_BAD_REQUEST)

        subscription = Follow.objects.create(
            subscriber=subscriber, author=author)
        serializer = FollowSerializer(
            subscription, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        subscriber = request.user
        author = get_object_or_404(User, id=id)
        subscription = Follow.objects.filter(
            subscriber=subscriber, author=author)
        if not subscription.exists():
            return Response(
                {'errors': 'Нет такой подписки'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
