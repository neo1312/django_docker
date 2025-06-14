from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inventory/', include('inventory.urls')),  # Include your app's URLs here
    path('', include('core.urls')),  # Include your app's URLs here
]

