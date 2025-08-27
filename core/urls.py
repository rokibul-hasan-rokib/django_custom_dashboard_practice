"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def api_root(request):
    """API root endpoint with available endpoints"""
    return JsonResponse({
        'message': 'Food Ordering System API',
        'version': '1.0',
        'endpoints': {
            'admin': '/admin/',
            'api': {
                'products': '/api/products/',
                'categories': '/api/categories/',
                'orders': '/api/orders/',
                'customers': '/api/customers/',
            }
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', api_root, name='api_root'),
    path('api/', include('product.urls')),
    path('api/', include('order.urls')),
    path('api/customers/', include('customer.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
