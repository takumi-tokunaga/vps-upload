"""
ASGI config for sugercraft project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sugercraft.settings')

from django.core.asgi import get_asgi_application
application = get_asgi_application()

# 静的ファイルの配信
from whitenoise import WhiteNoise
from .settings import BASE_DIR
application = WhiteNoise(application, root=os.path.join(BASE_DIR, 'staticfiles'))


# ここから下で Channels の設定や routing を import
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import participants.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            participants.routing.websocket_urlpatterns
        )
    ),
})
