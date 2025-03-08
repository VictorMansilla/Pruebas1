from django.db import models

class Usuarios(models.Model):
    class Roles(models.TextChoices):
        NORMAL = "normal", "Usuario Normal"
        ADMIN = "admin", "Administrador"

    usuario_nombre = models.CharField(null=False, unique=True, max_length=50)
    usuario_contrasegna = models.CharField(null=False, max_length=300)
    usuario_rol = models.CharField(
        max_length=10,
        choices=Roles.choices,
        default=Roles.NORMAL
    )

    def __str__(self) -> str:
        return f'{self.usuario_nombre} con el rol: {self.usuario_rol}'