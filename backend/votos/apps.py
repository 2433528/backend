from django.apps import AppConfig


class VotosConfig(AppConfig):
    name = 'votos'

    def ready(self):
        import votos.signals