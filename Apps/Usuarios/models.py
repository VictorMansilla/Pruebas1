from django.db import models

class Usuarios(models.Model):
    usuario_nombre = models.CharField(null=False, unique=True, max_length=50)
    usuario_contrasegna = models.CharField(null=False, max_length=300)
    
    def __str__(self) -> str:
        return self.usuario_nombre