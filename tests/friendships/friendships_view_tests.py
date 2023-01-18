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
    user3 = django_user_model.objects.create_user(
        username='user-three',
        email='userthree@gmail.com',
        password='password'
    )
    return {
        'user1': user1,
        'user2': user2,
        'user3': user3
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


def test_only_sender_can_cancel_friend_request(client: Client, django_user_model):
    """Only the sender of friend requests can cancel them"""
    test_users = create_users(django_user_model)
    user1, user2 = test_users['user1'], test_users['user2']
    user1_friend_request = FriendRequest.objects.create(sender=user1, receiver=user2)
    user2_friend_request = FriendRequest.objects.create(sender=user2, receiver=user1)
    # create notification for receiver of user1 friend request
    user1_friend_request.notifications.create(user=user2, verb='notification')
    client.force_login(user1)
    url = reverse('friendships:cancel-friend-request')
    response_1 = client.post(url, data={'pk': user1_friend_request.pk})
    response_2 = client.post(url, data={'pk': user2_friend_request.pk})
    assert response_1.status_code == HTTPStatus.OK
    assert not FriendRequest.objects.filter(pk=user1_friend_request.pk).exists()
    assert response_2.status_code == HTTPStatus.NOT_FOUND
    assert FriendRequest.objects.filter(pk=user2_friend_request.pk).exists()


def test_only_related_friends_can_unfriend_their_friendship(client: Client, django_user_model):
    """Only related friends can unfriend their friendship"""
    test_users = create_users(django_user_model)
    user1, user2, user3 = test_users['user1'], test_users['user2'], test_users['user3']
    user1.friendship.friends.add(user2)
    user2.friendship.friends.add(user1)
    client.force_login(user3)
    url = reverse('friendships:unfriend')
    response = client.post(url, data={'pk': user2.pk})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert user1.friendship.is_friend_with(user2)
    client.force_login(user1)
    response = client.post(url, data={'pk': user2.pk})
    assert response.status_code == HTTPStatus.OK
    assert not user1.friendship.is_friend_with(user2)


def test_user_friend_list_view(client: Client, django_user_model):
    """Test FriendListView"""
    test_users = create_users(django_user_model)
    user1, user2, user3 = test_users['user1'], test_users['user2'], test_users['user3']
    user1.friendship.friends.add(user2)
    user1.friendship.friends.add(user3)
    client.force_login(user2)
    url = reverse('friendships:friend_list', kwargs={'username': user1.username})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert response.context['page_obj'][0] == user3
    assert response.context['page_obj'][1] == user2
