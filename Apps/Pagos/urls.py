from django.urls import path
from .views import Hacer_Comprobante, Obtener_Registro_Comprobantes, Obtener_Comprobante, Descargar_Comprobante

urlpatterns = [
    path("Hacer_Comprobante/", Hacer_Comprobante, name='Hacer_Comprobante'),
    path("Obtener_Registro_Comprobantes/", Obtener_Registro_Comprobantes, name='Obtener_Registro_Comprobantes'),
    path("Obtener_Comprobante/<str:comprobante_numero>/", Obtener_Comprobante, name='Obtener_Comprobante'),
    path("Descargar_Comprobante/<str:comprobante_numero>/", Descargar_Comprobante, name='Descargar_Comprobante'),
]