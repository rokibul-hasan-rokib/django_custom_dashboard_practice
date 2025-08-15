from .models import Customer


def get_dashboard_data():
    return {
        'total_customers': Customer.objects.count(),
        'recent_customers': Customer.objects.order_by('-created_at')[:5],
        'customer_data': Customer.objects.all(),
    }