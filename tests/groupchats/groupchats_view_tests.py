import json
from http import HTTPStatus
from django.urls import reverse

from groupchats.models import GroupChatRoom, GroupChatRoomMessage




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
    gcr_obj = GroupChatRoom.objects.create(name='test_room', owner=user1)
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
    test_user = django_user_model.objects.create_user(
        username='test-user',
        password='password'
    )
    GroupChatRoom.objects.create(name='test_room', owner=test_user)
    url = reverse('groupchats:chat-room', kwargs={'room_name': 'test_room'})
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.FORBIDDEN


def create_group_chat_room_messages(django_user_model):
    user1 = django_user_model.objects.create_user(
        username='user-one',
        email='userone@gmail.com',
        password='password'
    )
    gcr_obj = GroupChatRoom.objects.create(name='test_room', owner=user1)
    gcr_obj.users.add(user1)
    gcrm_1 = GroupChatRoomMessage.objects.create(
        user=user1,
        room=gcr_obj,
        content='Hi There'
    )
    gcrm_1_dict = {
        'message': gcrm_1.content,
        'username': user1.username,
        'profile_image_url': user1.profile_image.url,
        'profile_url': user1.get_absolute_url(),
        'msg_timestamp': gcrm_1.timestamp.isoformat(),
        'msg_id': gcrm_1.id,
    }
    gcrm_2 = GroupChatRoomMessage.objects.create(
        user=user1,
        room=gcr_obj,
        content='Hi'
    )
    gcrm_2_dict = {
        'message': gcrm_2.content,
        'username': user1.username,
        'profile_image_url': user1.profile_image.url,
        'profile_url': user1.get_absolute_url(),
        'msg_timestamp': gcrm_2.timestamp.isoformat(),
        'msg_id': gcrm_2.id,
    }
    return user1, gcrm_1_dict, gcrm_2_dict


def test_get_chat_messages_without_earliest_msg_id_parameter(client, django_user_model):
    """
    Joined users (who are in users list of group chat room model) 
    can receive chat messages with or without earliest_msg_id parameter
    """
    user1, gcrm_1_dict, gcrm_2_dict = create_group_chat_room_messages(django_user_model)
    url = reverse('groupchats:chat-room-messages', kwargs={'room_name': 'test_room'})
    client.force_login(user1)
    response = client.get(url)
    response_data = json.loads(response.content)
    assert response.status_code == HTTPStatus.OK
    assert len(response_data) == 2
    assert response_data[0] == gcrm_2_dict
    assert response_data[1] == gcrm_1_dict


def test_get_chat_messages_with_earliest_msg_id_parameter(client, django_user_model):
    """
    Test GroupChatRoomMessageView pagination system
    """
    user1, gcrm_1_dict, gcrm_2_dict = create_group_chat_room_messages(django_user_model)
    url = reverse('groupchats:chat-room-messages', kwargs={'room_name': 'test_room'})
    client.force_login(user1)
    response = client.get(f"{url}?earliest_msg_id={gcrm_2_dict['msg_id']}")
    response_data = json.loads(response.content)
    assert response.status_code == HTTPStatus.OK
    assert len(response_data) == 1
    assert response_data[0] == gcrm_1_dict


def test_chat_room_message_view_return_404_for_not_registered_chat_rooms(admin_client):
    """
    GroupChatRoomMessageView return 404 status code for not registered chat rooms
    """
    url = reverse('groupchats:chat-room-messages', kwargs={'room_name': 'test_room'})
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    

def test_not_joined_users_to_group_chat_room_cannot_get_chat_messages(
    admin_client, django_user_model):
    """
    Return 403 status code for users who are not joined
    """
    test_user = django_user_model.objects.create_user(
        username='test-user',
        password='password'
    )
    GroupChatRoom.objects.create(name='test_room', owner=test_user)
    url = reverse('groupchats:chat-room-messages', kwargs={'room_name': 'test_room'})
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.FORBIDDEN
