from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from .models import Recipe, ShoppingCart


class IngredientFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author',)

    def get_is_favorited(self, queryset, name, value):
        if not value:
            return queryset
        favorites = self.request.user.favorites.all()
        return queryset.filter(
            pk__in=(favorite.recipe.pk for favorite in favorites)
        )

    def get_is_in_shopping_cart(self, queryset, name, value):
        if not value:
            return queryset
        try:
            recipes = (
                self.request.user.shopping_cart.recipes.all()
            )
        except ShoppingCart.DoesNotExist:
            return queryset
        return queryset.filter(
            pk__in=(recipe.pk for recipe in recipes)
        )
