"""
URLs para el módulo de operaciones
"""

from django.urls import path
from . import views

app_name = 'operations'

urlpatterns = [
    # Capacitaciones
    path('trainings/', views.training_list, name='training_list'),
    path('trainings/<int:pk>/', views.training_detail, name='training_detail'),
    path('trainings/<int:training_id>/enroll/', views.training_enroll, name='training_enroll'),
    path('my-trainings/', views.my_trainings, name='my_trainings'),

    # Servicios
    path('services/', views.service_list, name='service_list'),
    path('services/<int:pk>/', views.service_detail, name='service_detail'),

    # Planes de Operación
    path('plans/', views.operation_plan_list, name='operation_plan_list'),
    path('plans/<int:pk>/', views.operation_plan_detail, name='operation_plan_detail'),
    path('calendar/', views.operation_calendar, name='operation_calendar'),

    # Inventario
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/<int:pk>/', views.inventory_detail, name='inventory_detail'),
    path('inventory/request/create/', views.inventory_request_create, name='inventory_request_create'),

    # API Endpoints
    path('api/inventory/<int:item_id>/stock/', views.api_inventory_stock, name='api_inventory_stock'),

    # PDF Downloads
    path('trainings/<int:training_id>/certificate/download/', views.download_training_certificate, name='download_training_certificate'),
    path('services/<int:service_id>/report/download/', views.download_service_report, name='download_service_report'),
    path('inventory/report/download/', views.download_inventory_report, name='download_inventory_report'),
]
