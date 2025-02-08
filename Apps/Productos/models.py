from django.db import models

class Productos(models.Model):
    producto_codigo = models.CharField(null=False, max_length=150)
    producto_nombre = models.CharField(null=False, max_length=150)