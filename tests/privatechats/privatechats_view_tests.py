from http import HTTPStatus
from django.urls import reverse




def test_private_chat_room_return_200_for_view_loggedin_user(admin_client):
    """PrivateChatRoomView should return 200 status code for logged-in users"""
    url = reverse('privatechats:chat-room')
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK


