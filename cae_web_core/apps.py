from django.apps import AppConfig


class CaeWebCoreConfig(AppConfig):
    name = 'apps.CAE_Web.cae_web_core'
    verbose_name = 'CAE Web Core'

    def ready(self):
        # Connect siganls
        from . import signals
