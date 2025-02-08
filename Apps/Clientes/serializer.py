from rest_framework import serializers

from .models import Clientes

class ClientesSerializers(serializers.ModelSerializer):
    class Meta:
        model = Clientes
        fields = ['id', 'cliente_codigo', 'cliente_nombre', 'cliente_localidad']
        read_only_fields = ['id']


""" class ProductoSerializers(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id', 'producto_nombre', 'producto_precio', 'producto_descripcion', 'producto_usuario']
        read_only_fields = ['id', 'producto_usuario']
    

class user(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email'] """