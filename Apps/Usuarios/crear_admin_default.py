from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password
from .models import Usuarios
from dotenv import load_dotenv
import os

load_dotenv()

@receiver(post_migrate)
def crear_admin_default(sender, **kwargs):
    if not Usuarios.objects.filter(usuario_nombre=os.getenv('PRIMER_ADMIN_NOMBRE')).exists():
        Usuarios.objects.create(
            usuario_nombre=os.getenv('PRIMER_ADMIN_NOMBRE'),
            usuario_contrasegna=make_password(os.getenv('PRIMER_ADMIN_CONTRASEGNA')),
            usuario_rol='admin')