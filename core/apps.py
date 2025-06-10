from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from django.db.models.signals import post_migrate
        from . import signals
        post_migrate.connect(signals.grant_suspension_permission, sender=self)

