from django.apps import AppConfig


class GroupchatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'groupchats'

    def ready(self):
        import groupchats.signals
