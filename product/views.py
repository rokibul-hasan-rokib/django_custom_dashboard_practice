from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from .models import Category, Product, ProductImage
from .serializers import (
    CategorySerializer, CategoryListSerializer,
    ProductListSerializer, ProductDetailSerializer,
    ProductCreateSerializer, ProductUpdateSerializer,
    ProductStockSerializer, ProductImageSerializer
)
from .filters import ProductFilter
from .pagination import ProductPagination


class CategoryListCreateView(generics.ListCreateAPIView):
    """
    List all categories or create a new category
    """
    queryset = Category.objects.filter(is_active=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CategoryListSerializer
        return CategorySerializer

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    @method_decorator(vary_on_headers('Authorization'))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a category
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'pk'

    def perform_destroy(self, instance):
        """Soft delete by setting is_active to False"""
        instance.is_active = False
        instance.save()


class ProductListCreateView(generics.ListCreateAPIView):
    """
    List all products with advanced filtering or create a new product
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter
    ]
    filterset_class = ProductFilter
    search_fields = [
        'name', 'description', 'short_description', 
        'ingredients', 'category__name'
    ]
    ordering_fields = [
        'name', 'price', 'rating_average', 'created_at', 
        'sort_order', 'preparation_time'
    ]
    ordering = ['category__sort_order', 'sort_order', 'name']
    pagination_class = ProductPagination

    def get_queryset(self):
        """Get products with optimized queries"""
        queryset = Product.objects.select_related('category').filter(
            is_active=True
        )
        
        # Filter by category if specified
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__id=category)
        
        # Filter featured products
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Filter by availability
        available_only = self.request.query_params.get('available_only')
        if available_only and available_only.lower() == 'true':
            queryset = queryset.filter(
                availability='available',
                stock_quantity__gt=0
            )
        
        # Filter by dietary preferences
        vegetarian = self.request.query_params.get('vegetarian')
        if vegetarian and vegetarian.lower() == 'true':
            queryset = queryset.filter(is_vegetarian=True)
        
        vegan = self.request.query_params.get('vegan')
        if vegan and vegan.lower() == 'true':
            queryset = queryset.filter(is_vegan=True)
        
        gluten_free = self.request.query_params.get('gluten_free')
        if gluten_free and gluten_free.lower() == 'true':
            queryset = queryset.filter(is_gluten_free=True)
        
        # Price range filtering
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass
        
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductListSerializer
        return ProductCreateSerializer

    @method_decorator(cache_page(60 * 10))  # Cache for 10 minutes
    @method_decorator(vary_on_headers('Authorization'))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a product
    """
    queryset = Product.objects.select_related('category').prefetch_related(
        'additional_images'
    )
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductUpdateSerializer
        return ProductDetailSerializer

    def perform_destroy(self, instance):
        """Soft delete by setting is_active to False"""
        instance.is_active = False
        instance.save()


class FeaturedProductsView(generics.ListAPIView):
    """
    List featured products
    """
    serializer_class = ProductListSerializer
    permission_classes = []
    
    def get_queryset(self):
        return Product.objects.select_related('category').filter(
            is_active=True,
            is_featured=True,
            availability='available'
        )[:8]  # Limit to 8 featured products

    @method_decorator(cache_page(60 * 30))  # Cache for 30 minutes
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CategoryProductsView(generics.ListAPIView):
    """
    List products in a specific category
    """
    serializer_class = ProductListSerializer
    permission_classes = []
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'short_description']
    ordering_fields = ['name', 'price', 'rating_average', 'sort_order']
    ordering = ['sort_order', 'name']
    pagination_class = ProductPagination

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Product.objects.select_related('category').filter(
            category_id=category_id,
            is_active=True
        )


class ProductStockUpdateView(generics.UpdateAPIView):
    """
    Update product stock quantity and availability
    """
    queryset = Product.objects.all()
    serializer_class = ProductStockSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def patch(self, request, *args, **kwargs):
        product = self.get_object()
        action = request.data.get('action')
        quantity = request.data.get('quantity', 0)

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid quantity value'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if action == 'add':
            product.add_stock(quantity)
            message = f'Added {quantity} items to stock'
        elif action == 'reduce':
            if product.reduce_stock(quantity):
                message = f'Reduced stock by {quantity} items'
            else:
                return Response(
                    {'error': 'Insufficient stock'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return super().patch(request, *args, **kwargs)

        serializer = self.get_serializer(product)
        return Response({
            'message': message,
            'product': serializer.data
        })


class ProductSearchView(generics.ListAPIView):
    """
    Advanced product search with multiple criteria
    """
    serializer_class = ProductListSerializer
    permission_classes = []
    pagination_class = ProductPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if not query:
            return Product.objects.none()

        # Create search query
        search_query = Q(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query) |
            Q(ingredients__icontains=query) |
            Q(category__name__icontains=query)
        )

        return Product.objects.select_related('category').filter(
            search_query,
            is_active=True
        ).distinct()


@api_view(['GET'])
def product_statistics(request):
    """
    Get product statistics
    """
    cache_key = 'product_statistics'
    stats = cache.get(cache_key)
    
    if not stats:
        stats = {
            'total_products': Product.objects.filter(is_active=True).count(),
            'total_categories': Category.objects.filter(is_active=True).count(),
            'featured_products': Product.objects.filter(
                is_active=True, is_featured=True
            ).count(),
            'available_products': Product.objects.filter(
                is_active=True, 
                availability='available',
                stock_quantity__gt=0
            ).count(),
            'vegetarian_products': Product.objects.filter(
                is_active=True, is_vegetarian=True
            ).count(),
            'vegan_products': Product.objects.filter(
                is_active=True, is_vegan=True
            ).count(),
            'average_price': Product.objects.filter(
                is_active=True
            ).aggregate(avg_price=Avg('price'))['avg_price'] or 0,
            'categories_with_products': Category.objects.filter(
                is_active=True,
                products__is_active=True
            ).annotate(
                product_count=Count('products')
            ).values('name', 'product_count')
        }
        
        # Cache for 1 hour
        cache.set(cache_key, stats, 60 * 60)
    
    return Response(stats)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_update_products(request):
    """
    Bulk update multiple products
    """
    product_ids = request.data.get('product_ids', [])
    update_data = request.data.get('update_data', {})
    
    if not product_ids or not update_data:
        return Response(
            {'error': 'product_ids and update_data are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate allowed fields for bulk update
    allowed_fields = [
        'is_active', 'is_featured', 'availability', 
        'category', 'sort_order'
    ]
    
    invalid_fields = set(update_data.keys()) - set(allowed_fields)
    if invalid_fields:
        return Response(
            {'error': f'Invalid fields: {list(invalid_fields)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        updated_count = Product.objects.filter(
            id__in=product_ids
        ).update(**update_data)
        
        return Response({
            'message': f'Successfully updated {updated_count} products',
            'updated_count': updated_count
        })
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )