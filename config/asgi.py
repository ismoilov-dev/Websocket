"""
ASGI config for Real-Time Chat project.

Bu yerda HTTP va WebSocket protokollari ajratiladi:
- HTTP so'rovlari: Standart Django ASGI ilovasi orqali qayta ishlanadi.
- WebSocket so'rovlari: WebSocketJWTAuthMiddleware orqali autentifikatsiya qilinib,
  so'ngra ChatConsumer'ga yo'naltiriladi.

Arxitektura Oqimi:
HTTP:
  HTTP Request -> Django ASGI -> URLs -> Views

WebSocket:
  WebSocket Request
          ↓
  WebSocketJWTAuthMiddleware (Token tekshirish va scope['user'] ni to'ldirish)
          ↓
  URLRouter (ws/chat/ manzilini topish)
          ↓
  ChatConsumer (Ulanishni boshqarish va xabar almashish)
"""

import os
from django.core.asgi import get_asgi_application

# 1. Django muhit sozlamalarini o'rnatamiz
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 2. Django ASGI ilovasini ishga tushiramiz (Modellar yuklanishi uchun routingdan oldin bo'lishi shart!)
django_asgi_app = get_asgi_application()

# 3. Channels va loyiha modullarini Django yuklangandan so'ng import qilamiz
from channels.routing import ProtocolTypeRouter, URLRouter
from websocket.middlewares import WebSocketJWTAuthMiddleware
import websocket.routing

# 4. Asosiy ASGI dasturi
application = ProtocolTypeRouter({
    # Oddiy HTTP so'rovlari uchun
    "http": django_asgi_app,

    # Real-time WebSocket ulanishlari uchun
    "websocket": WebSocketJWTAuthMiddleware(
        URLRouter(
            websocket.routing.websocket_urlpatterns
        )
    ),
})
