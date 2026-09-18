from django.db import models
from django.conf import settings


class Message(models.Model):
    """
    Foydalanuvchilar tomonidan yuborilgan xabarlar modeli.
    REST API orqali qabul qilinib, ma'lumotlar bazasida saqlanadi,
    so'ngra Channels orqali WebSocket'ga tarqatiladi.
    """
    message = models.TextField(
        help_text="Xabar matni"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages",
        help_text="Xabarni yuborgan foydalanuvchi"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Xabar yaratilgan vaqt"
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = "Xabar"
        verbose_name_plural = "Xabarlar"

    def __str__(self):
        # Admin paneli yoki shell'da chiroyli ko'rinishi uchun
        return f"{self.user.username}: {self.message[:30]}"
