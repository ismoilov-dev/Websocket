from django.urls import path
from .views import index_view, MessageCreateAPIView

urlpatterns = [
    # Frontend asosiy sahifasi (Chat UI)
    path('', index_view, name='index'),

    # REST API xabar yuborish endpointi
    # POST /api/messages/
    path('api/messages/', MessageCreateAPIView.as_view(), name='message_create'),
]
