from rest_framework.pagination import PageNumberPagination


class LimitPagePagination(PageNumberPagination):
    """Фильтр пагинатора."""
    page_size_query_param = 'limit'
