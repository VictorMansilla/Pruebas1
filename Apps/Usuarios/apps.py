from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Apps.Usuarios'

    def ready(self):
        import Apps.Usuarios.crear_admin_default
        from .mantener_vivo_backend import scheduler