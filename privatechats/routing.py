from django.urls import path

from .consumers import PrivateChatConsumer


websocket_urlpatterns = [
    path('ws/privatechat/<str:roommate_name>/', PrivateChatConsumer.as_asgi()),
]