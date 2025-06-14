from django.shortcuts import render
from .models import Product

def test_app_template(request):
    return render(request, "test.html")  
