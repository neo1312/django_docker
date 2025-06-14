from django.urls import path
from . import views

urlpatterns = [
    path("test/app/", views.test_app_template, name="test_app"),
]
