from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from recipes import models


class UserSerializer(serializers.ModelSerializer):
    """Пользователи."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = models.User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed']

    def get_is_subscribed(self, obj):
        """Наличие подписки на полученного(ых) пользователя(ей)."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return models.Subscription.objects.filter(user=user,
                                                  author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    """Теги."""

    class Meta:
        model = models.Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    """Ингредиенты."""

    class Meta:
        model = models.Ingredient
        fields = ['id', 'name', 'measurement_unit']


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Ингредиенты в рецепте и их количество."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=models.Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = models.IngredientInRecipe
        fields = ('id', 'name', 'amount', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    """Рецепты."""
    author = UserSerializer(default=serializers.CurrentUserDefault())
    ingredients = IngredientInRecipeSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='_get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='_get_is_shopping_cart')
    image = Base64ImageField()

    class Meta:
        model = models.Recipe
        fields = ['id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time']

    def _get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return models.Favorite.objects.filter(user=user, recipe=obj).exists()

    def _get_is_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return models.ShoppingCard.objects.filter(user=user,
                                                  recipe=obj).exists()

    def validate(self, data):
        if len(data['ingredients']) < 1:
            raise serializers.ValidationError(
                {'errors': 'Необходимо указать хотябы один ингредиент!'}
            )
        ingredients = [ingredient['id'] for ingredient in data['ingredients']]
        if len(set(ingredients)) != len(ingredients):
            raise serializers.ValidationError(
                {'errors': 'Ингредиенты не должны повтряться!'}
            )
        if len(set(data['tags'])) != len(data['tags']):
            raise serializers.ValidationError(
                {'error': 'Теги не должны повторяться!'}
            )
        return data

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        # Добавить детализацию тегов.
        represent['tags'] = []
        for tag in instance.tags.all():
            represent['tags'].append(TagSerializer(tag).data)
        # Добавить детализацию ингредиентов.
        represent['ingredients'] = []
        for ingredient in instance.ingredients.all():
            data = IngredientSerializer(ingredient.ingredients).data
            data['amount'] = (
                IngredientInRecipeSerializer(ingredient).
                data['amount']
            )
            represent['ingredients'].append(data)
        return represent

    @staticmethod
    def _create_ingredients(recipe, validated_data):
        ingr_in_recipe = [
            models.IngredientInRecipe(recipes=recipe,
                                      ingredients=ingredient['id'],
                                      amount=ingredient['amount'])
            for ingredient in validated_data]
        models.IngredientInRecipe.objects.bulk_create(ingr_in_recipe)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        self._create_ingredients(recipe=recipe, validated_data=ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = super().update(instance, validated_data)
        models.IngredientInRecipe.objects.filter(recipes=recipe).all().delete()
        self._create_ingredients(recipe=recipe, validated_data=ingredients)
        return recipe


class FavoriteSerializer(serializers.ModelSerializer):
    """Избранное."""
    user = serializers.PrimaryKeyRelatedField(
        queryset=models.User.objects.all(),
        write_only=True
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=models.Recipe.objects.all(),
        write_only=True
    )
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = models.Favorite
        fields = ['user', 'recipe', 'id', 'name', 'image', 'cooking_time']
        read_only_fields = ['id', 'name', 'image', 'cooking_time']


class ShoppingCardSerializer(serializers.ModelSerializer):
    """Карта покупок."""
    user = serializers.PrimaryKeyRelatedField(
        queryset=models.User.objects.all(),
        write_only=True
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=models.Recipe.objects.all(),
        write_only=True
    )
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = models.ShoppingCard
        fields = ['user', 'recipe', 'id', 'name', 'image', 'cooking_time']
        read_only_fields = ['id', 'name', 'image', 'cooking_time']


class SubscribeRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов, для сериализатора подписок."""

    class Meta:
        model = models.Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class SubscribeSerializer(serializers.ModelSerializer):
    """Подписки на авторов."""
    user = serializers.PrimaryKeyRelatedField(
        queryset=models.User.objects.all(),
        default=serializers.CurrentUserDefault(),
        write_only=True
    )
    author = serializers.PrimaryKeyRelatedField(
        queryset=models.User.objects.all(),
        write_only=True
    )
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Subscription
        fields = ['user', 'author',
                  'id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count'
                  ]

    def get_recipes(self, obj):
        limit = self.context.get('request').GET.get('recipes_limit')
        limit = int(limit) if limit else None
        recipes = models.Recipe.objects.filter(author=obj.author)
        return SubscribeRecipesSerializer(recipes[:limit], many=True).data

    def get_recipes_count(self, obj):
        return models.Recipe.objects.filter(author=obj.author).count()

    def get_is_subscribed(self, obj):
        return models.Subscription.objects.filter(user=obj.user,
                                                  author=obj.author).exists()
