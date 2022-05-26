from os.path import abspath, dirname, join

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from fpdf import FPDF
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

from .models import (
    Ingredient,
    Tag,
    Recipe,
    Favorite,
    IngredientAmount,
    Cart,
)
from .filters import IngredientFilter, RecipeFilter
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeSerializer,
    RecipeShortReadSerializer,
)
from .permissions import IsOwnerOrReadOnly


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_class = RecipeFilter
    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_or_delete(self, request, model, id):
        if request.method == 'DELETE':
            obj = model.objects.filter(user=request.user, recipe__id=id)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Нет такого рецепта'},
                status=status.HTTP_400_BAD_REQUEST)
        if model.objects.filter(user=request.user, recipe__id=id).exists():
            return Response(
                {'errors': 'Рецепт уже добавлен'},
                status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=id)
        model.objects.create(user=request.user, recipe=recipe)
        serializer = RecipeShortReadSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        return self.add_or_delete(request, Favorite, pk)

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        return self.add_or_delete(request, Cart, pk)

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font(
            'DejaVuSans-Oblique',
            fname=join(dirname(abspath(__file__)), 'DejaVuSans-Oblique.ttf'))
        pdf.set_font('DejaVuSans-Oblique', size=25)
        ingredients = IngredientAmount.objects.filter(
            recipe__cart__user=request.user.id).values(
                'ingredient__name',
                'ingredient__measurement_unit').order_by(
                    'ingredient__name',
                    'ingredient__measurement_unit').annotate(
                    amount_sum=Sum('amount'))
        for n, ingredient in enumerate(ingredients, start=1):
            pdf.cell(
                0, 10,
                f'{n}. {ingredient["ingredient__name"]} '
                f'{ingredient["amount_sum"]} '
                f'{ingredient["ingredient__measurement_unit"]}',
                new_x='LMARGIN', new_y='NEXT')
        response = HttpResponse(
            bytes(pdf.output()), content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.pdf"')
        return response
