# srm/views.py

from django.shortcuts import render

def orderMainMenu(request):
    modules = [
        {"name": "Orden Automatica", "url": "auto/", "icon": "fas fa-shopping-cart"},
        {"name": "Orden Manual", "url": "/compras/", "icon": "fas fa-store"},
        {"name": "Historial", "url": "/clientes/", "icon": "fas fa-user-friends"},
        {"name": "Ultima", "url": "/reportes/", "icon": "fas fa-chart-bar"},
    ]
    return render(request, "orders.html", {"modules": modules})

def orderauto(request):
    return render(request, "ordersAuto.html")

