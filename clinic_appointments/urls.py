from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('homepage.urls')),
    path('cabinets/', include('cabinets.urls')),
    path('appointments/', include('appointments.urls')),
]
