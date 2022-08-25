from django.contrib import admin
from recipes.filters import IngredientFilterAdmin
from recipes.models import (Favorite, Ingredient, Recipe, ShoppingCard,
                            Subscription, Tag)


@admin.register(Subscription)
class Subscription(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author',)
    search_fields = ('user__username', 'author__username',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('slug',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit',)
    list_filter = (IngredientFilterAdmin,)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'text', 'cooking_time', 'image', 'author',)
    list_display_links = ('pk', 'name',)
    list_filter = ('author', 'name', 'tags', )
    search_fields = ('author__username', 'name',)
    empty_value_display = '-пусто-'

    @staticmethod
    def favorites(obj):
        return obj.favorite.filter(favorite=True).count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe',)


@admin.register(ShoppingCard)
class ShoppingCardAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe',)
