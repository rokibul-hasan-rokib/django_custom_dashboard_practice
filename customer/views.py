from django.shortcuts import render, redirect
from .forms import CustomerForm
from .models import Customer
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Customer
from .serializers import CustomerSerializer
from . import service

class CustomerListCreateView(generics.GenericAPIView):
    serializer_class = CustomerSerializer

    def get(self, request):
        customers = service.list_customers()
        serializer = self.serializer_class(customers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = service.create_customer(serializer.validated_data)
        return Response(self.serializer_class(customer).data, status=status.HTTP_201_CREATED)


class CustomerDetailView(generics.GenericAPIView):
    serializer_class = CustomerSerializer

    def get(self, request, pk):
        customer = service.get_customer(pk)
        serializer = self.serializer_class(customer)
        return Response(serializer.data)

    def put(self, request, pk):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = service.update_customer(pk, serializer.validated_data)
        return Response(self.serializer_class(customer).data)

    def delete(self, request, pk):
        service.delete_customer(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customer/customer_list.html', {'customers': customers})


def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    
    return render(request, 'customer/add_customer.html', {'form': form})


