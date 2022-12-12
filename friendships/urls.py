from django.urls import path

from . import views



app_name = 'friendships'

urlpatterns = [
    path('handle_friend_request/<int:pk>/', views.HandleFriendRequestView.as_view(), name='handle-friend-request'),
    path('send_friend_request/', views.SendFriendRequestView.as_view(), name='send-friend-request'),
]