from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Message
from .serializers import MessageSerializer


def index_view(request):
    """
    Real-Time Chat frontend sahifasini ko'rsatuvchi view.
    """
    return render(request, "websocket/index.html")


class MessageCreateAPIView(APIView):
    """
    Foydalanuvchi xabarlarini qabul qiluvchi va saqlab,
    WebSocket orqali real-time tarqatuvchi REST API endpointi.

    ARXITEKTURA OQIMI:
    User clicks Send / Swagger POST
            ↓
    POST /api/messages/
            ↓
    Django REST Framework (MessageCreateAPIView)
            ↓
    Message database'ga saqlanadi (SQLite)
            ↓
    channel_layer.group_send("user-{id}", {"type": "send_message", ...})
            ↓
    Channels Router & Group
            ↓
    ChatConsumer.send_message()
            ↓
    WebSocket Client (Browser)
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Yangi xabar yuborish (va WebSocket'ga uzatish)",
        description=(
            "Ushbu endpoint orqali yuborilgan xabar bazaga saqlanadi va "
            "darhol Channels InMemoryChannelLayer orqali foydalanuvchining "
            "WebSocket guruhiga ('user-{id}') yuboriladi."
        ),
        request=MessageSerializer,
        responses={
            201: OpenApiResponse(
                response=MessageSerializer,
                description="Xabar muvaffaqiyatli saqlandi va WebSocket orqali tarqatildi"
            ),
            400: OpenApiResponse(description="Noto'g'ri ma'lumot kiritildi"),
            401: OpenApiResponse(description="Avtorizatsiyadan o'tilmagan (JWT token kerak)"),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            # 1. Userni request.user dan olib, ma'lumotlar bazasiga saqlaymiz
            message_instance = serializer.save(user=request.user)

            # 2. Channels Channel Layer instansiyasini olamiz
            channel_layer = get_channel_layer()

            # 3. Foydalanuvchining unikal guruh nomini aniqlaymiz
            # Har bir foydalanuvchi faqat o'ziga tegishli guruhga a'zo bo'ladi: user-1, user-2, ...
            user_group = f"user-{request.user.id}"

            # 4. REST API orqali kelgan xabarni WebSocket groupiga yuboramiz.
            # "type": "send_message" event bo'lsa,
            # Channels ChatConsumer.send_message() methodini avtomatik chaqiradi.
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
            async_to_sync(channel_layer.group_send)(
                user_group,
                {
                    "type": "send_message",
                    "message": serializer.data,
                }
            )

            # 5. HTTP javobini 201 Created statusi bilan qaytaramiz
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
