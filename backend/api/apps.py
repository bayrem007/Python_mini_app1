from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self) -> None:
        from purbeurre.mongo import ensure_mongo_connected

        ensure_mongo_connected()
