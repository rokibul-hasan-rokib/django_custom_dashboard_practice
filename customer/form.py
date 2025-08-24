from django import form
from .models import Customer

class CustomerForm(form.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'