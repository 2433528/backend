from django.apps import AppConfig


class InfoConfig(AppConfig):
    name = 'info'

    def ready(self):
        import info.signals