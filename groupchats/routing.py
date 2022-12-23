from django.urls import path

from .consumers import GroupChatConsumer


websocket_urlpatterns = [
    path('ws/groupchat/<str:room_name>/', GroupChatConsumer.as_asgi()),
]