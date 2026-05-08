from math import ceil

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        count = self.page.paginator.count
        page_size = self.get_page_size(self.request) or self.page_size
        return Response(
            {
                "page": self.page.number,
                "page_size": page_size,
                "count": count,
                "total_pages": ceil(count / page_size) if page_size else 0,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )
