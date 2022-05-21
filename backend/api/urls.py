from rest_framework.routers import DefaultRouter
from django.urls import include, path

from .views import IngredientViewSet, TagViewSet, RecipeViewSet

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
v1_router.register(
    r'tags',
    TagViewSet,
    basename='tags'
)
v1_router.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
)


urlpatterns = [
    path('', include(v1_router.urls)),
]
