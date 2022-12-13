from http import HTTPStatus

from django.urls import reverse
from django.test import Client

from friendships.models import FriendRequest




def create_users(django_user_model):
    """Create some test users"""
    user1 = django_user_model.objects.create_user(
        username='user-one',
        email='userone@gmail.com',
        password='password'
    )
    user2 = django_user_model.objects.create_user(
        username='user-two',
        email='usertwo@gmail.com',
        password='password'
    )
    return {
        'user1': user1,
        'user2': user2
    }



def test_receiver_can_accept_friend_request(client: Client, django_user_model):
    """receiver can accept the friend request"""
    test_users = create_users(django_user_model)
    user1, user2 = test_users['user1'], test_users['user2']
    friend_req_obj = FriendRequest.objects.create(sender=user1, receiver=user2)
    client.force_login(user2)
    url = reverse('friendships:handle-friend-request', kwargs={'pk': friend_req_obj.pk})
    response = client.post(url, data={'accept': 'true'})
    assert response.status_code == HTTPStatus.OK
    assert user1.friendship.is_friend_with(user2)


def test_only_receiver_can_accept_friend_request(client: Client, django_user_model):
    """Only the receiver can accept the friend request"""
    test_users = create_users(django_user_model)
    user1, user2 = test_users['user1'], test_users['user2']
    friend_req_obj = FriendRequest.objects.create(sender=user1, receiver=user2)
    client.force_login(user1)
    url = reverse('friendships:handle-friend-request', kwargs={'pk': friend_req_obj.pk})
    response = client.post(url, data={'accept': 'true'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert not user1.friendship.is_friend_with(user2)


def test_receiver_can_decline_friend_request(client: Client, django_user_model):
    """receiver can decline the friend request"""
    test_users = create_users(django_user_model)
    user1, user2 = test_users['user1'], test_users['user2']
    friend_req_obj = FriendRequest.objects.create(sender=user1, receiver=user2)
    client.force_login(user2)
    url = reverse('friendships:handle-friend-request', kwargs={'pk': friend_req_obj.pk})
    response = client.post(url, data={'accept': 'false'})
    assert response.status_code == HTTPStatus.OK
    assert not user1.friendship.is_friend_with(user2)


def test_only_receiver_can_decline_friend_request(client: Client, django_user_model):
    """Only the receiver can decline the friend request"""
    test_users = create_users(django_user_model)
    user1, user2 = test_users['user1'], test_users['user2']
    friend_req_obj = FriendRequest.objects.create(sender=user1, receiver=user2)
    client.force_login(user1)
    url = reverse('friendships:handle-friend-request', kwargs={'pk': friend_req_obj.pk})
    response = client.post(url, data={'accept': 'false'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert not user1.friendship.is_friend_with(user2)


def test_send_friend_request(client: Client, django_user_model):
    """User can send friend request to other users"""
    test_users = create_users(django_user_model)
    user1, user2 = test_users['user1'], test_users['user2']
    client.force_login(user1)
    url = reverse('friendships:send-friend-request')
    response = client.post(url, data={'receiver_id': user2.id})
    assert response.status_code == HTTPStatus.OK


def test_send_friend_request_twice_make_conflict(client: Client, django_user_model):
    """Send friend request twice doesn't make two same friend request"""
    test_users = create_users(django_user_model)
    user1, user2 = test_users['user1'], test_users['user2']
    client.force_login(user1)
    url = reverse('friendships:send-friend-request')
    for _ in range(2):
        response = client.post(url, data={'receiver_id': user2.id})
    assert response.status_code == HTTPStatus.CONFLICT


def test_send_friend_request_to_dummy_user(client: Client, django_user_model):
    """Can't send friend request to dummy user"""
    test_users = create_users(django_user_model)
    user1= test_users['user1']
    client.force_login(user1)
    url = reverse('friendships:send-friend-request')
    response = client.post(url, data={'receiver_id': 33})
    assert response.status_code == HTTPStatus.NOT_FOUND