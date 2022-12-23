from django.urls import path

from . import views



app_name = 'groupchats'

urlpatterns = [
    path('room/<str:room_name>', views.GroupChatRoomView.as_view(), name='chat-room'),
]