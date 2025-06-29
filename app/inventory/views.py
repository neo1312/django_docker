from django.shortcuts import render
from django.db.models import Q
from .models import Product

def product_list(request):
    search_query = request.GET.get('q', '').strip()
    products = Product.objects.all().order_by('name')
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(variants__barcode__iexact=search_query)  # Exact barcode match
        ).distinct()  # Prevents duplicates
    
    # Keep your existing HTMX logic
    if request.headers.get('HX-Request'):
        return render(request, 'table.html', {'products': products})
    return render(request, 'list.html', {'products': products})
