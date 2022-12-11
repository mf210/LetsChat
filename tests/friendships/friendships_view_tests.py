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
    url = reverse('friendships:accept_friend', kwargs={'pk': friend_req_obj.pk})
    response = client.post(url)
    assert response.status_code == HTTPStatus.OK
    assert user1.friendship.is_friend_with(user2)


def test_only_receiver_can_accept_friend_request(client: Client, django_user_model):
    """Only the receiver can accept the friend request"""
    test_users = create_users(django_user_model)
    user1, user2 = test_users['user1'], test_users['user2']
    friend_req_obj = FriendRequest.objects.create(sender=user1, receiver=user2)
    client.force_login(user1)
    url = reverse('friendships:accept_friend', kwargs={'pk': friend_req_obj.pk})
    response = client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert not user1.friendship.is_friend_with(user2)

