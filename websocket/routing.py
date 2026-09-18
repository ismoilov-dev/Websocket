from django.urls import path
from .consumers import ChatConsumer

# WebSocket marshrutlari ro'yxati
# Klientlar ushbu manzil orqali WebSocket ulanishini amalga oshiradilar:
# ws://127.0.0.1:8000/ws/chat/?token=ACCESS_TOKEN
websocket_urlpatterns = [
    path("ws/chat/", ChatConsumer.as_asgi(), name="chat_ws"),
]
