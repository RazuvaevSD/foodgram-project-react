from rest_framework.pagination import PageNumberPagination


class LimitPagePagination(PageNumberPagination):
    """Фильтр пагинатора."""
    page_size = 10
    page_size_query_param = 'limit'
