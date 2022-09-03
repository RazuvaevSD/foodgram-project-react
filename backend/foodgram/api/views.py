from django.db.models import F, Sum
from django.http import FileResponse
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, ShoppingCard,
                            Subscription, Tag, User)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import (AuthorIdFilter, IngredientFilter, IsFavoritedFilter,
                      IsInShoppingCartFilter, TagsSlugFilter)
from .paginators import LimitPagePagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCardSerializer,
                          SubscribeSerializer, TagSerializer)
from .utils import add_object, del_object, generate_pdf_shopping_cart


class UserViewSet(DjoserUserViewSet):
    pagination_class = LimitPagePagination
    filter_backends = (filters.OrderingFilter, )
    ordering = ['id']

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        """Управление подпиской."""
        data = {'user': request.user.id,
                'author': get_object_or_404(User, id=id).id}
        if request.method == 'POST':
            # Добавить подписку.
            return add_object(serializer=SubscribeSerializer,
                              data=data,
                              context={'request': request})
        if request.method == 'DELETE':
            # Удалить подписку.
            return del_object(model=Subscription,
                              filters=data)
        return None

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Список авторов на которых подписан текущий пользователь."""
        subscribe = Subscription.objects.filter(user=request.user)
        page = self.paginate_queryset(subscribe)
        if page is not None:
            serializer = SubscribeSerializer(page, many=True,
                                             context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = SubscribeSerializer(subscribe,
                                         many=True,
                                         context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Список или один ингредиент (только чтение)."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
    filter_backends = (IngredientFilter, filters.OrderingFilter)
    search_fields = ('name',)
    ordering = ['name']


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Список или один тег (только чтение)."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAuthorOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Управление рецептами."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPagePagination
    filter_backends = (AuthorIdFilter, IsFavoritedFilter,
                       IsInShoppingCartFilter, TagsSlugFilter)
    filters_fields = ['author', 'is_favorited', 'is_in_shopping_cart', 'tags']

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        """Избранное."""
        data = {'user': request.user.id,
                'recipe': get_object_or_404(Recipe, pk=pk).pk}
        if request.method == 'POST':
            # Добавить в избранное.
            return add_object(data=data, serializer=FavoriteSerializer,
                              context={'request': request})
        if request.method == 'DELETE':
            # Удалить из избранного.
            return del_object(Favorite, data)
        return None

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        """Управление списком покупок"""
        data = {'user': request.user.id,
                'recipe': get_object_or_404(Recipe, pk=pk).pk}

        if request.method == 'POST':
            # Добавить в список покупок.
            return add_object(serializer=ShoppingCardSerializer, data=data,
                              context={'request': request})
        if request.method == 'DELETE':
            # Удалить из списка покупок.
            return del_object(model=ShoppingCard, filters=data)
        return None

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Получить файл со списком покупок"""
        shopping_card = (
            request.user.purchase.values(
                name=F('recipe__ingredients__ingredients__name'),
                measure=F('recipe__ingredients__ingredients__measurement_unit')
            ).annotate(amount=Sum('recipe__ingredients__amount'))
        )
        file_in_buffer = generate_pdf_shopping_cart(queryset=shopping_card)
        return FileResponse(file_in_buffer, as_attachment=True,
                            filename='shopping_cart.pdf')
