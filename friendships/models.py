from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation

from notifications.models import Notification



User = get_user_model()


class Friendship(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    friends = models.ManyToManyField(User, blank=True, related_name='friendships')

    def __str__(self):
        return self.user.username

    def is_friend_with(self, user):
        """Check friendship between self and passed user"""
        return self.friends.filter(pk=user.pk).exists()

    def unfriend(self, user):
        """Remove both users from each other friends list"""
        self.friends.remove(user)
        user.friendship.friends.remove(self.user)


class FriendRequest(models.Model):
    """
    A friend request consists of two main parts:
        1. SENDER
            - Person sending/initiating the friend request
        2. RECIVER
            - Person receiving the friend friend
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_reqs')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_reqs')
    creation_time = models.DateTimeField(auto_now_add=True)
    notifications = GenericRelation(Notification)

    def __str__(self):
        return f'{self.sender.username} -> {self.receiver.username}'
    
    def accept(self):
        """
        Accept a friend request.
        Update both SENDER and RECEIVER friendship.
        """
        self.receiver.friendship.friends.add(self.sender)
        self.sender.friendship.friends.add(self.receiver)
        self.delete()
