from django.db import models

class Clientes(models.Model):
    cliente_codigo = models.CharField(null=False, unique=True, max_length=80)
    cliente_nombre = models.CharField(null=False, max_length=150)
    cliente_localidad = models.CharField(null=True, max_length=250)