from django.db import models
from Apps.Usuarios.models import Usuarios
from Apps.Clientes.models import Clientes

class ReciboPago(models.Model):
    recibo_pago_numero = models.CharField(null=False, unique=True, editable=False)
    cliente = models.ForeignKey(Clientes, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    vendedor = models.ForeignKey(Usuarios, on_delete=models.PROTECT)
    factura_relacionada = models.CharField(null=False, max_length=30)
    fecha_factura = models.DateField(null=False)
    monto_recibido = models.IntegerField(null=False)
    opciones_medio_pago = (
        ('efectivo', 'EFECTIVO'),
        ('transferencia', 'TRANSFERENCIA'),
    )
    medio_de_pago = models.CharField(max_length=15, choices=opciones_medio_pago)
    transferido_a = models.CharField(null=True, max_length=100)
    fecha_transferencia = models.DateField(null=True)
    recibo_hasheado = models.CharField(null=False, max_length=300)

    def save(self, *args, **kwargs):
        if not self.recibo_pago_numero:
            ultimo_recibo_pago = ReciboPago.objects.order_by('-id').first()
            proximo_recibo_pago = f"{(ultimo_recibo_pago.id + 1) if ultimo_recibo_pago else 1:06d}"
            self.recibo_pago_numero = proximo_recibo_pago
        super().save(*args, **kwargs)

    def __str__(self):
        return self.recibo_pago_numero
    


class ImagenReciboPago(models.Model):
    recibo = models.ForeignKey(ReciboPago, on_delete=models.PROTECT, related_name='imagenes')
    url = models.URLField()