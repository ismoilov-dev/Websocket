from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    """
    Message modeli uchun serializer.
    Foydalanuvchi nomi avtomatik tarzda request.user dan olinadi,
    frontend faqat 'message' maydonini yuboradi.
    """
    # Foydalanuvchining faqat username'ini qaytaramiz (Frontend id yuborishi shart emas)
    user = serializers.CharField(source="user.username", read_only=True)
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Message
        fields = ['id', 'message', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
        extra_kwargs = {
            'message': {
                'help_text': 'Yuborilayotgan xabar matni'
            }
        }
