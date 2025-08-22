"""
ASGI config for outlinekerala project with WebSocket support.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from graphene_subscriptions.consumers import GraphqlSubscriptionConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'outlinekerala.settings')

# HTTP -> normal Django
django_asgi_app = get_asgi_application()

# ASGI application with WebSockets enabled
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("graphql/", GraphqlSubscriptionConsumer.as_asgi()),
        ])
    ),
})
