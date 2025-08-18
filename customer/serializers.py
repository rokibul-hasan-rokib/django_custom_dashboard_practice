from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"   # Or specify only required fields, e.g. ['id', 'name', 'email', 'created_at']
