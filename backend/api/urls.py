from rest_framework.routers import DefaultRouter
from django.urls import include, path

from .views import IngredientViewSet, TagViewSet, RecipeViewSet

v1_router = DefaultRouter()

v1_router.register(
    'ingredients/',
    IngredientViewSet,
    basename='ingredients'
)
v1_router.register(
    'tags/',
    TagViewSet,
    basename='tags'
)
v1_router.register(
    'recipes/',
    RecipeViewSet,
    basename='recipes'
)


urlpatterns = [
    path('', include(v1_router.urls)),
]
