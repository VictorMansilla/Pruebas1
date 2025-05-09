from rest_framework import serializers

from .models import Productos, RegistroPedidos

class ProductosSerializers(serializers.ModelSerializer):
    class Meta:
        model = Productos
        fields = ['id', 'producto_codigo', 'producto_nombre']
        read_only_fields = ['id']



class RegistroPedidosSerializers(serializers.ModelSerializer):
    class Meta:
        model = RegistroPedidos
        fields = ['id', 'pedido_numero', 'tipo', 'pedido_vendedor_id', 'pedido_vendedor_nombre', 'pedido_cliente_id', 'pedido_cliente_nombre', 'pedido_hora', 'pedido_productos_json', 'pedido_cables_json']
        read_only_fields = ['id']