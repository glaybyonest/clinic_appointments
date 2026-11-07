from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list_view, name='appointment_list'),
    # Маршрут статистики объявлен РАНЬШЕ маршрута с конвертером <slug:slug>,
    # чтобы адрес /appointments/statistics/ не интерпретировался как slug="statistics"
    path('statistics/', views.statistics_view, name='statistics'),
    path('<slug:slug>/', views.appointment_detail_view, name='appointment_detail'),
]
