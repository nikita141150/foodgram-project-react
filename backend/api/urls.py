from rest_framework.routers import DefaultRouter
from django.urls import include, path

from .views import IngredientViewSet, TagViewSet, RecipeViewSet

v1_router = DefaultRouter()

v1_router.register('tags', TagViewSet)
v1_router.register('ingredients', IngredientViewSet)
v1_router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(v1_router.urls)),
]
