from django.urls import path
from .views import Crear_Producto, Actualizar_Producto, Obtener_Productos, Hacer_Pedido, Obtener_Registro_Pedidos, Descargar_Registro_Pedidos, Obtener_Pedido, Descargar_Pedido, Obtener_Mi_Registro_Pedidos, Descargar_Mi_Registro_Pedidos

urlpatterns = [
    path("Crear_Producto/", Crear_Producto, name='Crear_Producto'),
    path("Actualizar_Producto/", Actualizar_Producto, name='Actualizar_Producto'),
    path("Obtener_Productos/", Obtener_Productos, name='Obtener_Productos'),
    path("Hacer_Pedido/", Hacer_Pedido, name='Hacer_Pedido'),
    path("Obtener_Registro_Pedidos/", Obtener_Registro_Pedidos, name='Obtener_Registro_Pedidos'),
    path("Descargar_Registro_Pedidos/", Descargar_Registro_Pedidos, name='Descargar_Registro_Pedidos'),
    path("Obtener_Pedido/<str:pedido_numero>/", Obtener_Pedido, name='Obtener_Pedido'),
    path("Descargar_Pedido/<str:pedido_numero>/", Descargar_Pedido, name='Descargar_Pedido'),
    path("Obtener_Mi_Registro_Pedidos/", Obtener_Mi_Registro_Pedidos, name='Obtener_Mi_Registro_Pedidos'),
    path("Descargar_Mi_Registro_Pedidos/", Descargar_Mi_Registro_Pedidos, name='Descargar_Mi_Registro_Pedidos'),
]