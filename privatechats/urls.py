from django.urls import path

from . import views



app_name = 'privatechats'
urlpatterns = [
    path('', views.PrivateChatRoomView.as_view(), name='chat-room'),
    path('room/<str:roommate>/messages/', views.PrivateChatRoomMessageView.as_view(), name='messages'),
]
