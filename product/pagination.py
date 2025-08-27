from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ProductPagination(PageNumberPagination):
    \"\"\"
    Custom pagination for product listings
    \"\"\"
    page_size = 12  # Default page size
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        \"\"\"
        Return paginated response with additional metadata
        \"\"\"
        return Response({
            'pagination': {
                'page': self.page.number,
                'pages': self.page.paginator.num_pages,
                'per_page': self.get_page_size(self.request),
                'total': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
            },
            'results': data
        })


class CategoryPagination(PageNumberPagination):
    \"\"\"
    Custom pagination for category listings
    \"\"\"
    page_size = 20  # Default page size for categories
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        \"\"\"
        Return paginated response with additional metadata
        \"\"\"
        return Response({
            'pagination': {
                'page': self.page.number,
                'pages': self.page.paginator.num_pages,
                'per_page': self.get_page_size(self.request),
                'total': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
            },
            'results': data
        })