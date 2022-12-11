from django.urls import path

from . import views



app_name = 'friendships'

urlpatterns = [
    path('accept_friend_request/<int:pk>/', views.AcceptFriendRequestView.as_view(), name='accept_friend')
]