from rest_framework.pagination import PageNumberPagination
from .constants import PAGE_SIZE


class CustomPageNumberPagination(PageNumberPagination):
    page_size = PAGE_SIZE
    page_query_param = 'page'
    page_size_query_param = 'limit'
