import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket ulanishlarini boshqaruvchi Asinxron Consumer.
    
    Vazifalari:
    1. Ulanishni tekshirish (JWT orqali scope["user"] authenticated ekanini aniqlash).
    2. Foydalanuvchini o'zining shaxsiy guruhiga (user-{id}) a'zo qilish.
    3. REST API'dan kelgan 'send_message' hodisasini qabul qilib, WebSocket klientiga yuborish.
    """

    async def connect(self):
        # 1. WebSocketga ulangan userni olamiz (JWT Middleware scope["user"] ga joylagan)
        self.user = self.scope.get("user")

        # 2. Foydalanuvchi authenticated ekanligini tekshiramiz
        if self.user is None or not self.user.is_authenticated:
            # Agar foydalanuvchi tizimga kirmagan yoki token yaroqsiz bo'lsa,
            # WebSocket ulanishni maxsus 4001 kodi bilan yopamiz.
            await self.close(code=4001)
            return

        # 3. Har bir user uchun alohida group yaratamiz
        # Masalan: user-1, user-2, user-3
        # Bu orqali xabarlar faqat shu foydalanuvchining o'ziga boradi
        self.room_group_name = f"user-{self.user.id}"

        # 4. Userni groupga qo'shamiz
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # 5. WebSocket ulanishini rasman qabul qilamiz (Handshake muvaffaqiyatli yakunlanadi)
        await self.accept()

        # 6. Klientga ulanish muvaffaqiyatli o'rnatilgani haqida birinchi xabarni yuboramiz
        await self.send(
            text_data=json.dumps({
                "type": "connection_established",
                "message": f"Assalomu alaykum, {self.user.username}! WebSocket ulanishi muvaffaqiyatli o'rnatildi.",
                "user": self.user.username,
                "user_id": self.user.id,
                "group": self.room_group_name
            }, ensure_ascii=False)
        )

    async def disconnect(self, close_code):
        # WebSocket yopilganda foydalanuvchini guruhdan chiqaramiz (tozalash)
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        """
        Bizning arxitekturamizda xabarlar WebSocket orqali yuborilmaydi,
        balki REST API (POST /api/messages/) orqali yuboriladi.
        Biroq, agar klient WebSocket orqali xabar yuborsa, unga qoidani eslatamiz.
        """
        await self.send(
            text_data=json.dumps({
                "type": "info",
                "message": "Xabarlarni WebSocket orqali emas, REST API (POST /api/messages/) orqali yuboring!",
            }, ensure_ascii=False)
        )

    # ==========================================================================
    # EVENT HANDLER: REST API -> group_send -> send_message
    # ==========================================================================
    # REST API views.py ichida:
    # channel_layer.group_send(user_group, {"type": "send_message", "message": data})
    # chaqirilganda, Channels avtomatik tarzda "send_message" nomli ushbu methodni chaqiradi.
    #
    # Flow:
    # REST API
    #    ↓
    # group_send()
    #    ↓
    # "type": "send_message"
    #    ↓
    # ChatConsumer.send_message()
    #    ↓
    # WebSocket client
    async def send_message(self, event):
        """
        Channel group'dan kelgan hodisani qabul qilib,
        WebSocket orqali haqiqiy browserga (klientga) jo'natamiz.
        """
        message_data = event.get("message")

        # WebSocket mijoziga JSON formatida uzatamiz
        await self.send(
            text_data=json.dumps({
                "type": "chat_message",
                "data": message_data
            }, ensure_ascii=False)
        )
