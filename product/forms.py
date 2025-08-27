from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from .models import Category, Product, ProductImage


class CategoryForm(forms.ModelForm):
    \"\"\"
    Form for creating and updating categories
    \"\"\"
    class Meta:
        model = Category
        fields = [
            'name', 'description', 'image', 'is_active', 'sort_order'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category description',
                'rows': 4
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'sort_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            })
        }
    
    def clean_name(self):
        \"\"\"Validate category name is unique (case-insensitive)\"\"\"
        name = self.cleaned_data['name']
        existing = Category.objects.filter(name__iexact=name)
        
        if self.instance and self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise ValidationError('Category with this name already exists.')
        
        return name


class ProductForm(forms.ModelForm):
    \"\"\"
    Form for creating and updating products
    \"\"\"
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
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter detailed product description',
                'rows': 5
            }),
            'short_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter brief description'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'original_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'image_alt': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Alt text for image'
            }),
            'availability': forms.Select(attrs={
                'class': 'form-control'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'ingredients': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'List ingredients separated by commas',
                'rows': 3
            }),
            'allergens': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'List allergens separated by commas'
            }),
            'spice_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'calories': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'preparation_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Minutes'
            }),
            'protein': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'placeholder': 'Grams'
            }),
            'carbs': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'placeholder': 'Grams'
            }),
            'fat': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'placeholder': 'Grams'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_vegetarian': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_vegan': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_gluten_free': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO title'
            }),
            'meta_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO description'
            }),
            'sort_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter categories to only active ones
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
    
    def clean(self):
        \"\"\"Custom validation for the form\"\"\"
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        original_price = cleaned_data.get('original_price')
        availability = cleaned_data.get('availability')
        stock_quantity = cleaned_data.get('stock_quantity')
        
        # Validate pricing
        if original_price and price and original_price <= price:
            raise ValidationError({
                'original_price': 'Original price must be greater than current price.'
            })
        
        # Validate stock vs availability
        if availability == 'available' and stock_quantity == 0:
            raise ValidationError({
                'availability': 'Cannot set as available when stock quantity is 0.'
            })
        
        return cleaned_data
    
    def clean_name(self):
        \"\"\"Validate product name is unique within category\"\"\"
        name = self.cleaned_data['name']
        category = self.cleaned_data.get('category')
        
        if category:
            existing = Product.objects.filter(
                name__iexact=name,
                category=category
            )
            
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError(
                    'Product with this name already exists in this category.'
                )
        
        return name
    
    def save(self, commit=True):
        \"\"\"Save product with auto-generated slug\"\"\"
        product = super().save(commit=False)
        
        if not product.slug or (self.instance and self.instance.name != product.name):
            base_slug = slugify(product.name)
            slug = base_slug
            counter = 1
            
            while Product.objects.filter(slug=slug).exclude(pk=product.pk).exists():
                slug = f\"{base_slug}-{counter}\"
                counter += 1
            
            product.slug = slug
        
        if commit:
            product.save()
        
        return product


class ProductImageForm(forms.ModelForm):
    \"\"\"
    Form for adding additional product images
    \"\"\"
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'sort_order']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Alt text for image'
            }),
            'sort_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            })
        }


class ProductFilterForm(forms.Form):
    \"\"\"
    Form for filtering products in admin or frontend
    \"\"\"
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        empty_label=\"All Categories\",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price',
            'step': '0.01'
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price',
            'step': '0.01'
        })
    )
    
    availability = forms.ChoiceField(
        choices=[('', 'All')] + Product.AVAILABILITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    spice_level = forms.ChoiceField(
        choices=[('', 'All')] + Product.SPICE_LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    is_vegetarian = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    is_vegan = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    is_gluten_free = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    is_featured = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class StockUpdateForm(forms.Form):
    \"\"\"
    Form for updating product stock
    \"\"\"
    ACTION_CHOICES = [
        ('add', 'Add Stock'),
        ('reduce', 'Reduce Stock'),
        ('set', 'Set Stock Level')
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    quantity = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Quantity'
        })
    )
    
    def clean_quantity(self):
        \"\"\"Validate quantity is positive\"\"\"
        quantity = self.cleaned_data['quantity']
        if quantity < 0:
            raise ValidationError('Quantity must be positive.')
        return quantity