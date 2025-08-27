from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from decimal import Decimal
import uuid


class Category(models.Model):
    """
    Product category model for organizing food items
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, help_text="Category name")
    description = models.TextField(blank=True, help_text="Category description")
    image = models.ImageField(
        upload_to='categories/', 
        blank=True, 
        null=True,
        help_text="Category image"
    )
    is_active = models.BooleanField(default=True, help_text="Is category active?")
    sort_order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product:category_detail', kwargs={'pk': self.pk})

    @property
    def active_products_count(self):
        """Count of active products in this category"""
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    """
    Product model for food items in the ordering system
    """
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
        ('limited', 'Limited Stock'),
    ]

    SPICE_LEVEL_CHOICES = [
        ('none', 'No Spice'),
        ('mild', 'Mild'),
        ('medium', 'Medium'),
        ('hot', 'Hot'),
        ('extra_hot', 'Extra Hot'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text="Product name")
    slug = models.SlugField(max_length=200, unique=True, help_text="URL slug")
    description = models.TextField(help_text="Product description")
    short_description = models.CharField(
        max_length=300, 
        blank=True,
        help_text="Brief product description"
    )
    
    # Pricing
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Product price"
    )
    original_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Original price (for discount display)"
    )
    
    # Category relationship
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products',
        help_text="Product category"
    )
    
    # Images
    image = models.ImageField(
        upload_to='products/', 
        help_text="Main product image"
    )
    image_alt = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Alt text for main image"
    )
    
    # Availability and stock
    availability = models.CharField(
        max_length=20, 
        choices=AVAILABILITY_CHOICES, 
        default='available',
        help_text="Product availability status"
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Available stock quantity"
    )
    
    # Food-specific attributes
    ingredients = models.TextField(
        blank=True,
        help_text="List of ingredients"
    )
    allergens = models.CharField(
        max_length=300,
        blank=True,
        help_text="Allergen information"
    )
    spice_level = models.CharField(
        max_length=20,
        choices=SPICE_LEVEL_CHOICES,
        default='none',
        help_text="Spice level"
    )
    calories = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Calories per serving"
    )
    preparation_time = models.PositiveIntegerField(
        default=15,
        help_text="Preparation time in minutes"
    )
    
    # Nutritional information
    protein = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Protein content in grams"
    )
    carbs = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Carbohydrate content in grams"
    )
    fat = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Fat content in grams"
    )
    
    # Status and visibility
    is_active = models.BooleanField(
        default=True,
        help_text="Is product active and visible?"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Is this a featured product?"
    )
    is_vegetarian = models.BooleanField(
        default=False,
        help_text="Is this product vegetarian?"
    )
    is_vegan = models.BooleanField(
        default=False,
        help_text="Is this product vegan?"
    )
    is_gluten_free = models.BooleanField(
        default=False,
        help_text="Is this product gluten-free?"
    )
    
    # SEO and metadata
    meta_title = models.CharField(
        max_length=200, 
        blank=True,
        help_text="SEO meta title"
    )
    meta_description = models.CharField(
        max_length=300, 
        blank=True,
        help_text="SEO meta description"
    )
    
    # Ordering and display
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Display order within category"
    )
    
    # Ratings and reviews
    rating_average = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Average rating (0-5)"
    )
    review_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of reviews"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['category__sort_order', 'sort_order', 'name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['is_featured', 'is_active']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product:product_detail', kwargs={'slug': self.slug})

    @property
    def is_available(self):
        """Check if product is available for ordering"""
        return (
            self.is_active and 
            self.availability == 'available' and 
            self.stock_quantity > 0
        )

    @property
    def discount_percentage(self):
        """Calculate discount percentage if original price exists"""
        if self.original_price and self.original_price > self.price:
            return round(
                ((self.original_price - self.price) / self.original_price) * 100
            )
        return 0

    @property
    def is_on_sale(self):
        """Check if product is on sale"""
        return self.original_price and self.original_price > self.price

    def reduce_stock(self, quantity):
        """Reduce stock quantity and update availability"""
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            if self.stock_quantity == 0:
                self.availability = 'unavailable'
            elif self.stock_quantity < 10:  # Low stock threshold
                self.availability = 'limited'
            self.save(update_fields=['stock_quantity', 'availability'])
            return True
        return False

    def add_stock(self, quantity):
        """Add stock quantity and update availability"""
        self.stock_quantity += quantity
        if self.stock_quantity > 0 and self.availability == 'unavailable':
            self.availability = 'available'
        self.save(update_fields=['stock_quantity', 'availability'])

    def update_rating(self, new_rating):
        """Update average rating with new rating"""
        total_rating = self.rating_average * self.review_count + new_rating
        self.review_count += 1
        self.rating_average = round(total_rating / self.review_count, 2)
        self.save(update_fields=['rating_average', 'review_count'])


class ProductImage(models.Model):
    """
    Additional product images model
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='additional_images'
    )
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return f"{self.product.name} - Image {self.sort_order}"
