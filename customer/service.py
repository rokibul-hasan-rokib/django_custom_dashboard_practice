from .models import Customer
from django.shortcuts import get_object_or_404


def get_dashboard_data():
    return {
        'total_customers': Customer.objects.count(),
        'recent_customers': Customer.objects.order_by('-created_at')[:5],
        'customer_data': Customer.objects.all(),
    }
    
def list_customers():
    return Customer.objects.all()

def get_customer(customer_id: int):
    return get_object_or_404(Customer, id=customer_id)


def create_customer(data: dict):
    return Customer.objects.create(**data)


def update_customer(customer_id: int, data: dict):
    customer = get_object_or_404(Customer, id=customer_id)
    for field, value in data.items():
        setattr(customer, field, value)
    customer.save()
    return customer

def delete_customer(customer_id: int):
    customer = get_customer(customer_id)
    customer.delete()
    return True

