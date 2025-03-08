from django.db import models

class Productos(models.Model):
    producto_codigo = models.CharField(null=False, max_length=150)
    producto_nombre = models.CharField(null=False, max_length=150)



class RegistroPedidos(models.Model):
    pedido_numero = models.CharField(null=False, unique=True, editable=False)
    pedido_vendedor_id = models.IntegerField(null=False)
    pedido_vendedor_nombre = models.CharField(null=False, max_length=100)
    pedido_cliente_id = models.IntegerField(null=False)
    pedido_cliente_nombre = models.CharField(null=False, max_length=200)
    pedido_hora = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pedido_numero:
            ultimo_pedido = RegistroPedidos.objects.order_by('-id').first()
            proximo_pedido = f"{(ultimo_pedido.id + 1) if ultimo_pedido else 1:010d}"
            self.pedido_numero = proximo_pedido
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pedido {self.pedido_numero}"

    class Meta:
        ordering = ['-id']