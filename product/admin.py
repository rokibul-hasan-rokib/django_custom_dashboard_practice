from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count
from .models import Category, Product, ProductImage
from .forms import CategoryForm, ProductForm, ProductImageForm


class ProductImageInline(admin.TabularInline):
    """
    Inline admin for product additional images
    """
    model = ProductImage
    form = ProductImageForm
    extra = 1
    max_num = 10
    fields = ['image', 'alt_text', 'sort_order', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        """Display image preview in admin"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for Category model
    """
    form = CategoryForm
    list_display = [
        'name', 'product_count', 'is_active', 'sort_order', 
        'image_preview', 'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'sort_order']
    ordering = ['sort_order', 'name']
    readonly_fields = ['created_at', 'updated_at', 'product_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Settings', {
            'fields': ('is_active', 'sort_order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def image_preview(self, obj):
        """Display image preview in list view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 50px; max-height: 50px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Image"
    
    def product_count(self, obj):
        """Display count of products in category"""
        count = obj.products.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:product_product_changelist')
            return format_html(
                '<a href="{}?category__id__exact={}">{} products</a>',
                url, obj.id, count
            )
        return "0 products"
    product_count.short_description = "Products"
    
    def get_queryset(self, request):
        """Optimize queryset with product count"""
        qs = super().get_queryset(request)
        return qs.annotate(product_count=Count('products'))


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface for Product model
    """
    form = ProductForm
    inlines = [ProductImageInline]
    
    list_display = [
        'name', 'category', 'price', 'stock_status', 'availability', 
        'rating_display', 'is_featured', 'is_active', 'image_preview'
    ]
    list_filter = [
        'category', 'availability', 'spice_level', 'is_active', 
        'is_featured', 'is_vegetarian', 'is_vegan', 'is_gluten_free',
        'created_at'
    ]
    search_fields = [
        'name', 'description', 'short_description', 'ingredients', 
        'slug', 'category__name'
    ]
    list_editable = ['price', 'availability', 'is_featured', 'is_active']
    ordering = ['category__sort_order', 'sort_order', 'name']
    readonly_fields = [
        'slug', 'rating_average', 'review_count', 'created_at', 
        'updated_at', 'image_preview_large'
    ]
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description', 'short_description')
        }),
        ('Pricing', {
            'fields': ('price', 'original_price')
        }),
        ('Media', {
            'fields': ('image', 'image_alt', 'image_preview_large')
        }),
        ('Inventory', {
            'fields': ('availability', 'stock_quantity')
        }),
        ('Food Details', {
            'fields': (
                'ingredients', 'allergens', 'spice_level', 'calories', 
                'preparation_time'
            ),
            'classes': ('collapse',)
        }),
        ('Nutrition', {
            'fields': ('protein', 'carbs', 'fat'),
            'classes': ('collapse',)
        }),
        ('Dietary Information', {
            'fields': ('is_vegetarian', 'is_vegan', 'is_gluten_free')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'is_featured', 'sort_order')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('rating_average', 'review_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def image_preview(self, obj):
        """Display small image preview in list view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 40px; max-height: 40px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Image"
    
    def image_preview_large(self, obj):
        """Display large image preview in detail view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.image.url
            )
        return "No image"
    image_preview_large.short_description = "Image Preview"
    
    def stock_status(self, obj):
        """Display stock status with color coding"""
        if obj.stock_quantity == 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">Out of Stock ({})</span>',
                obj.stock_quantity
            )
        elif obj.stock_quantity < 10:
            return format_html(
                '<span style="color: orange; font-weight: bold;">Low Stock ({})</span>',
                obj.stock_quantity
            )
        else:
            return format_html(
                '<span style="color: green;">In Stock ({})</span>',
                obj.stock_quantity
            )
    stock_status.short_description = "Stock"
    
    def rating_display(self, obj):
        """Display rating with stars"""
        if obj.rating_average > 0:
            stars = '★' * int(obj.rating_average) + '☆' * (5 - int(obj.rating_average))
            return format_html(
                '<span title="{} stars ({} reviews)">{}</span>',
                obj.rating_average, obj.review_count, stars
            )
        return "No ratings"
    rating_display.short_description = "Rating"
    
    def get_queryset(self, request):
        """Optimize queryset with related objects"""
        qs = super().get_queryset(request)
        return qs.select_related('category')
    
    actions = [
        'mark_as_active', 'mark_as_inactive', 'mark_as_featured', 
        'mark_as_not_featured', 'mark_as_available', 'mark_as_unavailable'
    ]
    
    def mark_as_active(self, request, queryset):
        """Mark selected products as active"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} products marked as active.")
    mark_as_active.short_description = "Mark selected products as active"
    
    def mark_as_inactive(self, request, queryset):
        """Mark selected products as inactive"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} products marked as inactive.")
    mark_as_inactive.short_description = "Mark selected products as inactive"
    
    def mark_as_featured(self, request, queryset):
        """Mark selected products as featured"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} products marked as featured.")
    mark_as_featured.short_description = "Mark selected products as featured"
    
    def mark_as_not_featured(self, request, queryset):
        """Mark selected products as not featured"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"{updated} products marked as not featured.")
    mark_as_not_featured.short_description = "Remove featured status from selected products"
    
    def mark_as_available(self, request, queryset):
        """Mark selected products as available"""
        updated = queryset.update(availability='available')
        self.message_user(request, f"{updated} products marked as available.")
    mark_as_available.short_description = "Mark selected products as available"
    
    def mark_as_unavailable(self, request, queryset):
        """Mark selected products as unavailable"""
        updated = queryset.update(availability='unavailable')
        self.message_user(request, f"{updated} products marked as unavailable.")
    mark_as_unavailable.short_description = "Mark selected products as unavailable"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    Admin interface for ProductImage model
    """
    list_display = ['product', 'image_preview', 'alt_text', 'sort_order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['product__name', 'alt_text']
    list_editable = ['alt_text', 'sort_order']
    ordering = ['product', 'sort_order']
    
    def image_preview(self, obj):
        """Display image preview in list view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 60px; max-height: 60px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"


# Customize admin site header and title
admin.site.site_header = "Food Ordering System Admin"
admin.site.site_title = "Food Admin"
admin.site.index_title = "Welcome to Food Ordering System Administration"