from django.urls import path
from . import views

app_name = 'cabinets'

urlpatterns = [
    path('', views.cabinet_list_view, name='cabinet_list'),
]
