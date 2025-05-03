"""
ASGI config for djangoBackend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from channels.auth import AuthMiddlewareStack
import saloon.routing 

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoBackend.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            saloon.routing.websocket_urlpatterns
        )
    ),
})