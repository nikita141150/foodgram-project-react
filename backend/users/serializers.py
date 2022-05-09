from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from api.models import Recipe
from .models import User, Follow


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password',
            'is_subscribed',
        )
        write_only_fields = ('password',)
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'is_subscribed': {'required': False},
        }

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()

    def create(self, validated_data):
        validated_data['password'] = (
            make_password(validated_data.pop('password'))
        )
        return super().create(validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для краткого отображения сведений о рецепте
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(CustomUserSerializer):
    """
    Сериализатор для вывода подписок пользователя
    """
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True).data
