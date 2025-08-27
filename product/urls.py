from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    # Category URLs
    path('categories/', views.CategoryListCreateView.as_view(), name='category_list'),
    path('categories/<uuid:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('categories/<uuid:category_id>/products/', views.CategoryProductsView.as_view(), name='category_products'),
    
    # Product URLs
    path('products/', views.ProductListCreateView.as_view(), name='product_list'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/<slug:slug>/stock/', views.ProductStockUpdateView.as_view(), name='product_stock'),
    
    # Special product endpoints
    path('products/featured/', views.FeaturedProductsView.as_view(), name='featured_products'),
    path('products/search/', views.ProductSearchView.as_view(), name='product_search'),
    
    # Utility endpoints
    path('statistics/', views.product_statistics, name='product_statistics'),
    path('bulk-update/', views.bulk_update_products, name='bulk_update_products'),
]