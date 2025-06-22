from rest_framework import serializers

from .models import ReciboPago, ImagenReciboPago



class ImagenReciboPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenReciboPago
        fields = ['url']



class ComprobantesSerializers(serializers.ModelSerializer):
    cliente_codigo = serializers.CharField(source='cliente.cliente_codigo', read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.cliente_nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='vendedor.usuario_nombre', read_only=True)
    imagenes = ImagenReciboPagoSerializer(many=True, read_only=True)
    
    class Meta:
        model = ReciboPago
        fields = ['id',
                  'recibo_pago_numero',
                  'cliente',
                  'cliente_codigo',
                  'cliente_nombre',
                  'fecha',
                  'vendedor',
                  'usuario_nombre',
                  'factura_relacionada',
                  'fecha_factura',
                  'monto_recibido',
                  'medio_de_pago',
                  'transferido_a',
                  'fecha_transferencia',
                  'recibo_hasheado',
                  'imagenes']
        read_only_fields = ['id']