from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()


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
        ordering = ['-id']
        indexes = [
            models.Index(fields=['slug', ]),
            models.Index(fields=['name', ]),
        ]


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
        ordering = ['-id']
        indexes = [
            models.Index(fields=['name', ]),
        ]


class IngredientInRecipe(models.Model):
    """Модель 'Ингредиент рецепта'"""
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='recipes',
        verbose_name='Рецепт',
    )
    recipes = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1), ],
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=('ingredients', 'recipes'),
                name='unique_ingredients_in_recipe',
            ),
        ]
        indexes = [
            models.Index(fields=['ingredients', ]),
            models.Index(fields=['recipes', ]),
            models.Index(fields=['recipes', 'ingredients', ]),
        ]


class Recipe(models.Model):
    """Модель 'Рецепт'"""
    name = models.CharField(
        max_length=200,
        verbose_name='Наименование',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    cooking_time = models.PositiveIntegerField(
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
        ordering = ['-id']
        indexes = [
            models.Index(fields=['name', ]),
            models.Index(fields=['author', ]),
        ]


class Favorite(models.Model):
    """Модель 'Избранное'"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_review_favorite',
            ),
        ]
        indexes = [
            models.Index(fields=['user', ]),
            models.Index(fields=['recipe', ]),
            models.Index(fields=['user', 'recipe', ]),
        ]


class ShoppingCard(models.Model):
    """Модель 'Корзина'"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchase',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='purchase',
        verbose_name='Купить',
    )

    class Meta:
        verbose_name = 'Корзина'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_review_shopping_card',
            ),
        ]
        indexes = [
            models.Index(fields=['user', ]),
            models.Index(fields=['recipe', ]),
            models.Index(fields=['user', 'recipe', ]),
        ]


class Subscription(models.Model):
    """Модель 'Подписчики'"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписки'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_review_subscription',
            ),
            models.CheckConstraint(
                # Запрет подписки на себя
                check=~models.Q(user=models.F("author")),
                name="forbidden_subscript_self",
            ),
        ]
        indexes = [
            models.Index(fields=['user', ]),
            models.Index(fields=['author', ]),
            models.Index(fields=['user', 'author', ]),
        ]
