from django.urls import path
from .views import Crear_Cliente, Obtener_Clientes

urlpatterns = [
    path("Crear_Cliente/", Crear_Cliente, name='Crear_Cliente'),
    path("Obtener_Clientes/", Obtener_Clientes, name='Obtener_Clientes'),
]