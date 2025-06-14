# core/views.py

from django.shortcuts import render

def home(request):
    modules = [
        {"name": "Ventas", "url": "/ventas/", "icon": "fas fa-shopping-cart"},
        {"name": "Compras", "url": "/compras/", "icon": "fas fa-store"},
        {"name": "Devoluciones", "url": "/devoluciones/", "icon": "fas fa-undo"},
        {"name": "Cotizaciones", "url": "/cotizaciones/", "icon": "fas fa-file-invoice-dollar"},
        {"name": "Órdenes", "url": "/ordenes/", "icon": "fas fa-clipboard-list"},
        {"name": "Presupuestos", "url": "/presupuestos/", "icon": "fas fa-coins"},
        {"name": "Clientes", "url": "/clientes/", "icon": "fas fa-user-friends"},
        {"name": "Reportes", "url": "/reportes/", "icon": "fas fa-chart-bar"},
    ]
    return render(request, "home.html", {"modules": modules})

