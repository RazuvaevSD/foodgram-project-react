from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    """Модель 'Ингредиент'"""
    name = models.CharField(
        max_length=200,
        verbose_name='Наименование',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'


class Tag(models.Model):
    """Модель 'Тег'"""
    name = models.CharField(
        max_length=200,
        verbose_name='Наименование',
    )
    color = models.CharField(
        max_length=7,
        validators=[
            RegexValidator(
                # Проверка маски: 3-х или 6-и значные HEX-коды
                regex='^#(([a-zA-Z0-9]{6})|([a-zA-Z0-9]{3}))$',
                message=('Поле не соответствует формату HEX-кода '
                         '^#(([a-zA-Z0-9]{6})|([a-zA-Z0-9]{3}))$'),
            ),
        ],
        verbose_name='Цвет',
    )
    slug = models.SlugField(
        unique=True,
        validators=[
            RegexValidator(
                regex='^[-a-zA-Z0-9_]+$',
                message=('Поле не соответствует формату slug '
                         '^[-a-zA-Z0-9_]+$'),
            ),
        ],
    )

    class Meta:
        verbose_name = 'Тег'


class Recipe(models.Model):
    """Модель 'Рецепт'"""
    name = models.CharField(
        max_length=200,
        verbose_name='Наименование',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1), ],
        verbose_name='Время приготовления в минутах',
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )

    class Meta:
        verbose_name = 'Рецепт'


class RecipeIngredient(models.Model):
    """Модель 'Ингредиент рецепта'"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.RESTRICT,
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_review_recipe_ingredient',
            ),
        ]


class Favorite(models.Model):
    """Модель 'Избранное'"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_review_favorite',
            ),
        ]


class ShoppingCard(models.Model):
    """Модель 'Корзина'"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_review_shopping_card',
            ),
        ]


class Subscription(models.Model):
    """Модель 'Подписчики'"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='Пользователь',
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='Подписчик',
    )

    class Meta:
        verbose_name = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'subscriber'),
                name='unique_review_subscription',
            ),
            models.CheckConstraint(
                # Запрет подписки на себя
                check=~~models.Q(user=models.F("subscriber")),
                name="forbidden_subscript_self",
            ),
        ]
