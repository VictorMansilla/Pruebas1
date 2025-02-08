from django.urls import path
from .views import Crear_Usuario, Validar_Usuario

urlpatterns = [
    path("Crear_Usuario/", Crear_Usuario, name='Crear_Usuario'),
    path("Validar_Usuario/", Validar_Usuario, name='Validar_Usuario'),
]