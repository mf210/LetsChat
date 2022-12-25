from http import HTTPStatus
from django.urls import reverse

from groupchats.models import GroupChatRoom




def test_group_chat_room_view_return_not_found_for_not_existing_chat_room(admin_client):
    """
    GroupChatRoom view return 404 (Not Found) status code for not existing chat room
    """
    url = reverse('groupchats:chat-room', kwargs={'room_name': 'test_room'})
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_joined_users_to_group_chat_room_gets_ok_status_code(client, django_user_model):
    """
    Http status code should be 200 just if group chat room is exist
    and user is joined to the group chat room
    """
    user1 = django_user_model.objects.create_user(
        username='user-one',
        email='userone@gmail.com',
        password='password'
    )
    gcr_obj = GroupChatRoom.objects.create(name='test_room')
    gcr_obj.users.add(user1)
    client.force_login(user1)
    url = reverse('groupchats:chat-room', kwargs={'room_name': 'test_room'})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_not_joined_user_to_group_chat_room_gets_forbidden_status_code(
    admin_client, django_user_model):
    """
    Get 403 (Forbidden) status code
    for users who are not in the group_chat_room users list
    """
    GroupChatRoom.objects.create(name='test_room')
    url = reverse('groupchats:chat-room', kwargs={'room_name': 'test_room'})
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.FORBIDDEN