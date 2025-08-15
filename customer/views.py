from django.shortcuts import render, redirect
from .forms import CustomerForm


def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    
    return render(request, 'customer/add_customer.html', {'form': form})