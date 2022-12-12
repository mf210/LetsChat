import pytest
from django.contrib.auth import get_user_model

from friendships.models import Friendship, FriendRequest




USER_MODEL = get_user_model()





@pytest.mark.django_db
class FriendshipModelTests:
    """
    Friendship Model Tests
    """
    def create_users(self):
        user1 = USER_MODEL.objects.create_user(
            username='user-one',
            email='userone@gmail.com',
            password='password'
        )
        user2 = USER_MODEL.objects.create_user(
            username='user-two',
            email='usertwo@gmail.com',
            password='password'
        )
        return {
            'user1': user1,
            'user2': user2
        }

    def test_str_method(self):
        """Test __str__ method"""
        user1 = self.create_users()['user1']
        assert str(user1.friendship) == user1.username

    def test_add_friend(self):
        """Add a new friend"""
        users = self.create_users()
        user1, user2 = users['user1'], users['user2']
        assert user1.friendship.friends.count() == 0
        user1.friendship.add_friend(user2)
        assert user1.friendship.friends.count() == 1
        assert user1.friendship.is_friend_with(user2)

    def test_remove_friend(self):
        """Remove a friend from user's friend list"""
        users = self.create_users()
        user1, user2 = users['user1'], users['user2']
        user1.friendship.add_friend(user2)
        user1.friendship.remove_friend(user2)
        assert not user1.friendship.is_friend_with(user2)
    
    def test_unfriend(self):
        """Unfriending user"""
        users = self.create_users()
        user1, user2 = users['user1'], users['user2']
        user1.friendship.add_friend(user2)
        user2.friendship.add_friend(user1)
        user1.friendship.unfriend(user2)
        assert not user1.friendship.is_friend_with(user2)
        assert not user2.friendship.is_friend_with(user1)



@pytest.mark.django_db
class FriendRequestModelTests:
    """Test FriendRequest Model"""
    def create_users(self):
        user1 = USER_MODEL.objects.create_user(
            username='user-one',
            email='userone@gmail.com',
            password='password'
        )
        user2 = USER_MODEL.objects.create_user(
            username='user-two',
            email='usertwo@gmail.com',
            password='password'
        )
        return user1, user2

    def create_friendreq_obj(self):
        user1, user2 = self.create_users()
        return FriendRequest.objects.create(sender=user1, receiver=user2)

    def test_str_method(self):
        """Test __str__ method"""
        user1, user2 = self.create_users()
        friendreq_obj = FriendRequest(sender=user1, receiver=user2)
        assert 'user-one -> user-two' == str(friendreq_obj)

    def test_accept_friend_request(self):
        """Accept a friend request"""
        user1, user2 = self.create_users()
        friendreq_obj = FriendRequest(sender=user1, receiver=user2)
        friendreq_obj.accept()
        assert not friendreq_obj.is_active
        assert user1.friendship.is_friend_with(user2)
        assert user2.friendship.is_friend_with(user1)

    def test_decline_friend_request(self):
        """Decline a friend request"""
        friendreq_obj = self.create_friendreq_obj()
        friendreq_obj.decline()
        assert not friendreq_obj.is_active

    def test_cancel_friend_request(self):
        """Cancel a friend request"""
        friendreq_obj = self.create_friendreq_obj()
        friendreq_obj.cancel()
        assert not friendreq_obj.is_active
