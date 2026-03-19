from django.apps import AppConfig


class ComunicadosConfig(AppConfig):
    name = 'comunicados'

    def ready(self):
        import comunicados.signals 