from rest_framework import pagination


class LimitOffsetPagination(pagination.LimitOffsetPagination):
    max_limit = 5000
