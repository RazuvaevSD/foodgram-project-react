from django.contrib import admin

from recipes.filters import IngredientFilterAdmin
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCard, Subscription, Tag)


@admin.register(Subscription)
class Subscription(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author',)
    list_display_links = ('pk', 'user', 'author')
    search_fields = ('user__username', 'author__username',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug',)
    list_display_links = ('pk', 'name')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('slug',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit',)
    list_display_links = ('pk', 'name')
    list_filter = (IngredientFilterAdmin,)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ['pk', 'recipes', 'ingredients',
                    'measurement_unit', 'amount']
    readonly_fields = ['measurement_unit']
    list_display_links = ('pk', 'recipes', 'ingredients')
    search_fields = ('recipes__name', 'ingredients__name')

    def measurement_unit(self, obj):
        return obj.ingredients.measurement_unit
    measurement_unit.short_description = 'Единица измерения'


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    list_display = ['pk', 'recipes', 'ingredients',
                    'measurement_unit', 'amount']
    readonly_fields = ['measurement_unit']
    extra = 1
    min_num = 1
    max_num = 1

    def measurement_unit(self, obj):
        return obj.ingredients.measurement_unit
    measurement_unit.short_description = 'Единица измерения'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'text', 'cooking_time', 'image', 'author',
                    'favorites')
    list_display_links = ('pk', 'name',)
    list_filter = ('author', 'name', 'tags', )
    search_fields = ('author__username', 'name', 'tags__name')
    empty_value_display = '-пусто-'
    inlines = (IngredientInRecipeInline,)

    @staticmethod
    def favorites(obj):
        return obj.favorites.filter(user=obj.author).count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe',)
    list_display_links = ('pk', 'user', 'recipe')


@admin.register(ShoppingCard)
class ShoppingCardAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe',)
    list_display_links = ('pk', 'user', 'recipe')
