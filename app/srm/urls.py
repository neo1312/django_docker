from django.urls import path
from . import views

urlpatterns = [
    path("order/", views.orderMainMenu, name="orderMainMenu"),
    path("order/auto/", views.orderauto, name="orderauto"),
]
