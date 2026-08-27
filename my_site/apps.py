from django.apps import AppConfig

class MySiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'my_site'
    verbose_name = 'Управление сайтом'

    def ready(self):
        from . import checks  # noqa: F401
