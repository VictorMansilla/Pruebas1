from django.urls import path
from .views import Crear_Producto, Obtener_Productos, Hacer_Pedido, Obtener_Registro_Pedidos

urlpatterns = [
    path("Crear_Producto/", Crear_Producto, name='Crear_Producto'),
    path("Obtener_Productos/", Obtener_Productos, name='Obtener_Productos'),
    path("Hacer_Pedido/", Hacer_Pedido, name='Hacer_Pedido'),
    path("Obtener_Registro_Pedidos/", Obtener_Registro_Pedidos, name='Obtener_Registro_Pedidos'),
]