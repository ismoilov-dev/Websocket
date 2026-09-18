"""
WebSocket JWT Authentication Middleware.

MUHIM ESLATMA:
"Query-string JWT usuli faqat educational/demo maqsadida ishlatilmoqda.
Production'da token URL'da ko‘rinib qolishi mumkin."

Production muhitida tokenni WebSocket subprotocol, cookie yoki ulanishdan so'ng
dastlabki auth-xabar orqali uzatish tavsiya etiladi.
"""

from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()


@database_sync_to_async
def get_user_from_db(user_id):
    """
    Ma'lumotlar bazasidan berilgan user_id bo'yicha foydalanuvchini olish.
    Asinxron Channels ichida synchronous ORM so'rovini xavfsiz bajarish
    uchun database_sync_to_async bilan o'ralgan.
    """
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class WebSocketJWTAuthMiddleware:
    """
    WebSocket ulanish so'rovi (scope) kelganda query-string'dan 'token'ni
    ajratib olib, SimpleJWT orqali foydalanuvchini aniqlovchi Middleware.
    
    Ulanish namunasi:
    ws://127.0.0.1:8000/ws/chat/?token=eyJhbGciOi...
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # 1. Faqat WebSocket so'rovlari uchun ishlaymiz
        if scope["type"] == "websocket":
            # 2. query_string ni olamiz (bayt shaklida bo'ladi, masalan: b'token=xyz')
            query_string = scope.get("query_string", b"").decode("utf-8")
            query_params = parse_qs(query_string)

            # 3. tokenni ajratib olamiz
            token_list = query_params.get("token")
            token = token_list[0] if token_list else None

            if token:
                try:
                    # 4. SimpleJWT AccessToken orqali tokenni tekshiramiz (yaroqlilik va imzo)
                    access_token = AccessToken(token)

                    # 5. Token ichidagi user_id ni olamiz
                    user_id = access_token.get("user_id")

                    # 6. Database'dan userni topamiz
                    if user_id is not None:
                        scope["user"] = await get_user_from_db(user_id)
                    else:
                        scope["user"] = AnonymousUser()

                except (InvalidToken, TokenError, Exception):
                    # Agar token muddati o'tgan, soxta yoki noto'g'ri bo'lsa
                    scope["user"] = AnonymousUser()
            else:
                # Token berilmagan bo'lsa
                scope["user"] = AnonymousUser()

        # Keyingi middleware yoki consumer'ga uzatamiz
        return await self.inner(scope, receive, send)
