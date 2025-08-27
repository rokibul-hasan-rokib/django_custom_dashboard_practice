from rest_framework import serializers
from django.utils.text import slugify
from .models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model with product count
    """
    active_products_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'image', 'is_active', 
            'sort_order', 'active_products_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        """Ensure category name is unique (case-insensitive)"""
        if Category.objects.filter(name__iexact=value).exists():
            if self.instance and self.instance.name.lower() != value.lower():
                raise serializers.ValidationError("Category with this name already exists.")
            elif not self.instance:
                raise serializers.ValidationError("Category with this name already exists.")
        return value


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for category listings
    """
    active_products_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'active_products_count']


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for product additional images
    """
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'sort_order']
        read_only_fields = ['id']


class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for product listings
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_available = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    is_on_sale = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'price', 
            'original_price', 'image', 'category_name', 'is_available',
            'discount_percentage', 'is_on_sale', 'rating_average', 
            'review_count', 'is_featured', 'is_vegetarian', 'is_vegan',
            'is_gluten_free', 'spice_level', 'preparation_time'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for product details
    """
    category = CategoryListSerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True)
    additional_images = ProductImageSerializer(many=True, read_only=True)
    is_available = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    is_on_sale = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'price', 'original_price', 'category', 'category_id',
            'image', 'image_alt', 'availability', 'stock_quantity',
            'ingredients', 'allergens', 'spice_level', 'calories',
            'preparation_time', 'protein', 'carbs', 'fat',
            'is_active', 'is_featured', 'is_vegetarian', 'is_vegan',
            'is_gluten_free', 'meta_title', 'meta_description',
            'sort_order', 'rating_average', 'review_count',
            'additional_images', 'is_available', 'discount_percentage',
            'is_on_sale', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'rating_average', 'review_count', 
            'created_at', 'updated_at'
        ]

    def validate(self, data):
        """Custom validation for product data"""
        # Validate pricing
        price = data.get('price')
        original_price = data.get('original_price')
        
        if original_price and price and original_price <= price:
            raise serializers.ValidationError({
                'original_price': 'Original price must be greater than current price.'
            })
        
        # Validate stock vs availability
        availability = data.get('availability')
        stock_quantity = data.get('stock_quantity', 0)
        
        if availability == 'available' and stock_quantity == 0:
            raise serializers.ValidationError({
                'availability': 'Cannot set as available when stock quantity is 0.'
            })
        
        return data

    def validate_name(self, value):
        """Ensure product name is unique within category"""
        category_id = self.initial_data.get('category_id')
        if category_id:
            existing = Product.objects.filter(
                name__iexact=value, 
                category_id=category_id
            )
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise serializers.ValidationError(
                    "Product with this name already exists in this category."
                )
        return value

    def create(self, validated_data):
        """Create product with auto-generated slug"""
        if not validated_data.get('slug'):
            validated_data['slug'] = slugify(validated_data['name'])
        
        # Ensure slug is unique
        base_slug = validated_data['slug']
        slug = base_slug
        counter = 1
        
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        validated_data['slug'] = slug
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update product with slug regeneration if name changed"""
        if 'name' in validated_data and validated_data['name'] != instance.name:
            new_slug = slugify(validated_data['name'])
            base_slug = new_slug
            counter = 1
            
            while Product.objects.filter(slug=new_slug).exclude(pk=instance.pk).exists():
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            
            validated_data['slug'] = new_slug
        
        return super().update(instance, validated_data)


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new products
    """
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'short_description', 'price', 
            'original_price', 'category', 'image', 'image_alt',
            'availability', 'stock_quantity', 'ingredients', 'allergens',
            'spice_level', 'calories', 'preparation_time', 'protein',
            'carbs', 'fat', 'is_active', 'is_featured', 'is_vegetarian',
            'is_vegan', 'is_gluten_free', 'meta_title', 'meta_description',
            'sort_order'
        ]

    def create(self, validated_data):
        """Create product with auto-generated slug"""
        validated_data['slug'] = slugify(validated_data['name'])
        
        # Ensure slug is unique
        base_slug = validated_data['slug']
        slug = base_slug
        counter = 1
        
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        validated_data['slug'] = slug
        return super().create(validated_data)


class ProductUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing products
    """
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'short_description', 'price', 
            'original_price', 'category', 'image', 'image_alt',
            'availability', 'stock_quantity', 'ingredients', 'allergens',
            'spice_level', 'calories', 'preparation_time', 'protein',
            'carbs', 'fat', 'is_active', 'is_featured', 'is_vegetarian',
            'is_vegan', 'is_gluten_free', 'meta_title', 'meta_description',
            'sort_order'
        ]

    def update(self, instance, validated_data):
        """Update product with slug regeneration if name changed"""
        if 'name' in validated_data and validated_data['name'] != instance.name:
            new_slug = slugify(validated_data['name'])
            base_slug = new_slug
            counter = 1
            
            while Product.objects.filter(slug=new_slug).exclude(pk=instance.pk).exists():
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            
            instance.slug = new_slug
        
        return super().update(instance, validated_data)


class ProductStockSerializer(serializers.ModelSerializer):
    """
    Serializer for stock management operations
    """
    class Meta:
        model = Product
        fields = ['stock_quantity', 'availability']

    def validate(self, data):
        """Validate stock and availability consistency"""
        availability = data.get('availability')
        stock_quantity = data.get('stock_quantity')
        
        if availability == 'available' and stock_quantity == 0:
            raise serializers.ValidationError(
                "Cannot set as available when stock quantity is 0."
            )
        
        return data