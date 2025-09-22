from django.apps import AppConfig

class SrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'srm'

    def ready(self):
        import srm.signals  # This triggers the signal registration
