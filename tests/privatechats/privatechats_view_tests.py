import json
from http import HTTPStatus
from django.urls import reverse

from privatechats.models import PrivateChatRoom, PrivateChatRoomMessage



def test_private_chat_room_return_200_for_view_loggedin_user(admin_client):
    """PrivateChatRoomView should return 200 status code for logged-in users"""
    url = reverse('privatechats:chat-room')
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK


def create_group_chat_room_messages(django_user_model):
    user1 = django_user_model.objects.create_user(
        username='user1',
        email='user1@gmail.com',
        password='password'
    )
    user2 = django_user_model.objects.create_user(
        username='user2',
        email='user2@gmail.com',
        password='password'
    )
    # make user1 and user2 friends
    user1.friendship.friends.add(user2)
    user2.friendship.friends.add(user1)
    # Create PrivateChatRoom objects
    pcr_obj = PrivateChatRoom.objects.create(name='user1user2')
    pcrm_1 = PrivateChatRoomMessage.objects.create(
        user=user1,
        room=pcr_obj,
        content='Hi'
    )
    pcrm_1_dict = {
        'message': pcrm_1.content,
        'username': user1.username,
        'profile_image_url': user1.profile_image.url,
        'profile_url': user1.get_absolute_url(),
        'msg_timestamp': pcrm_1.timestamp.ctime(),
        'msg_id': pcrm_1.id,
    }
    pcrm_2 = PrivateChatRoomMessage.objects.create(
        user=user2,
        room=pcr_obj,
        content='By'
    )
    pcrm_2_dict = {
        'message': pcrm_2.content,
        'username': user2.username,
        'profile_image_url': user2.profile_image.url,
        'profile_url': user2.get_absolute_url(),
        'msg_timestamp': pcrm_2.timestamp.ctime(),
        'msg_id': pcrm_2.id,
    }
    return user1, user2, pcrm_1_dict, pcrm_2_dict


def test_get_chat_messages_without_earliest_msg_id_parameter(client, django_user_model):
    """
    Friends users can receive chat messages with or without earliest_msg_id parameter
    """
    user1, user2, gcrm_1_dict, gcrm_2_dict = create_group_chat_room_messages(django_user_model)
    client.force_login(user1)
    url = reverse('privatechats:messages', kwargs={'roommate': 'user2'})
    response = client.get(url)
    response_data = json.loads(response.content)
    assert response.status_code == HTTPStatus.OK
    assert len(response_data) == 2
    assert response_data[0] == gcrm_2_dict
    assert response_data[1] == gcrm_1_dict


def test_get_chat_messages_with_earliest_msg_id_parameter(client, django_user_model):
    """
    Test PrivateChatRoomMessageView pagination system
    """
    user1, user2, gcrm_1_dict, gcrm_2_dict = create_group_chat_room_messages(django_user_model)
    client.force_login(user1)
    url = reverse('privatechats:messages', kwargs={'roommate': 'user2'})
    response = client.get(f"{url}?earliest_msg_id={gcrm_2_dict['msg_id']}")
    response_data = json.loads(response.content)
    assert response.status_code == HTTPStatus.OK
    assert len(response_data) == 1
    assert response_data[0] == gcrm_1_dict


def test_private_chat_room_message_view_return_404_for_non_existence_users(admin_client):
    """
    PrivateChatRoomMessageView return 404 status code for non existence users
    """
    url = reverse('privatechats:messages', kwargs={'roommate': 'user3'})
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    

def test_not_friends_users_cannot_get_private_chat_messages(
    admin_client, django_user_model):
    """
    Return 403 status code for users who are not friends
    """
    django_user_model.objects.create_user(
        username='user1',
        email='user1@gmail.com',
        password='password'
    )
    url = reverse('privatechats:messages', kwargs={'roommate': 'user1'})
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.FORBIDDEN

