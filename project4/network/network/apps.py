from django.apps import AppConfig


class NetworkConfig(AppConfig):
    name = "network"

    def ready(self) -> None:
        # Implicitly connect a signal handlers decorated with @receiver.
        from . import signals
