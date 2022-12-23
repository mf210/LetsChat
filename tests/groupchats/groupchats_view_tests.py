from http import HTTPStatus
from django.urls import reverse

from groupchats.models import GroupChatRoom





def test_group_chat_room_view_status_code(admin_client):
    """Http status code should be 200 just for existing chat-rooms"""
    url = reverse('groupchats:chat-room', kwargs={'room_name': 'public'})
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    GroupChatRoom.objects.create(name='public')
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK
