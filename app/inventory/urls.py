from django.urls import path
from . import views

urlpatterns = [
    path("ventas/", views.product_list, name="product_list"),
]
