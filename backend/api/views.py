from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import viewsets, permissions
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework import status

from .models import (
    Ingredient,
    Tag,
    Recipe,
    Favorite,
    IngredientAmount,
    ShoppingCart
)
from .filters import IngredientFilter, RecipeFilter
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    RecipeShortReadSerializer,
    ShoppingCartSerializer,
)
from .permissions import IsAuthorOrAdminOrReadOnly


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny)
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend, IngredientFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny)
    queryset = Tag.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete',)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = RecipeReadSerializer(
            instance=serializer.instance,
            context={'request': self.request}
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer = RecipeReadSerializer(
            instance=serializer.instance,
            context={'request': self.request},
        )
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )

    def add_to_favorite(self, request, recipe):
        try:
            Favorite.objects.create(user=request.user, recipe=recipe)
        except IntegrityError:
            return Response(
                {'errors': 'Вы уже сделали подписку'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = RecipeShortReadSerializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def delete_from_favorite(self, request, recipe):
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
        if not favorite.exists():
            return Response(
                {'errors': 'Вы не делали подписку'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('get', 'delete',),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'GET':
            return self.add_to_favorite(request, recipe)
        return self.delete_from_favorite(request, recipe)

    @action(detail=True, methods=["POST"],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=ShoppingCart)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        final_list = {}
        ingredients = IngredientAmount.objects.filter(
            recipe__carts__user=request.user).values_list(
            'ingredient__name', 'ingredient__measurement_unit',
            'amount'
        )
        for item in ingredients:
            name = item[0]
            if name not in final_list:
                final_list[name] = {
                    'measurement_unit': item[1],
                    'amount': item[2]
                }
            else:
                final_list[name]['amount'] += item[2]
        pdfmetrics.registerFont(
            TTFont('Handicraft', 'data/Handicraft.ttf', 'UTF-8'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.pdf"')
        page = canvas.Canvas(response)
        page.setFont('Handicraft', size=24)
        page.drawString(200, 800, 'Список покупок')
        page.setFont('Handicraft', size=16)
        height = 750
        for i, (name, data) in enumerate(final_list.items(), 1):
            page.drawString(75, height, (f'{i}. {name} - {data["amount"]} '
                                         f'{data["measurement_unit"]}'))
            height -= 25
        page.showPage()
        page.save()
        return response
