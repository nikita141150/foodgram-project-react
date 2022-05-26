from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple

from .models import (
    Favorite,
    Ingredient,
    IngredientAmount,
    Recipe,
    Tag,
    Cart
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class IngredientsInline(admin.TabularInline):
    model = Recipe.ingredients.through
    raw_id_fields = ('ingredient',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'number_favorites')
    list_filter = ('author', 'name', 'tags')
    inlines = (IngredientsInline,)
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple}}

    def number_favorites(self, obj):
        return obj.favorites.count()
    number_favorites.short_description = 'Добавлений в избранное'


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'recipe', 'amount')
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    empty_value_display = '-пусто-'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    empty_value_display = '-пусто-'
