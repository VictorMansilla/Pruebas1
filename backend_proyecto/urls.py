from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Usuarios/', include('Apps.Usuarios.urls')),
    path('Clientes/', include('Apps.Clientes.urls')),
    path('Productos/', include('Apps.Productos.urls'))
]
