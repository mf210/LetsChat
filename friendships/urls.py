from django.urls import path

from . import views



app_name = 'friendships'

urlpatterns = [
    path('handle_friend_request/<int:pk>/', views.HandleFriendRequestView.as_view(), name='handle-friend-request')
]