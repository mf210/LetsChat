from django.db import models
from django.contrib.auth import get_user_model


USER_MODEL = get_user_model()



class Friendship(models.Model):
    user = models.OneToOneField(USER_MODEL, on_delete=models.CASCADE)
    friends = models.ManyToManyField(USER_MODEL, blank=True, related_name='friends')

    def __str__(self):
        return self.user.username

    def add_friend(self, user):
        """Add a new friend"""
        if not self.friends.filter(pk=user.pk).exists():
            self.friends.add(user)

    def is_friend_with(self, user):
        """Check friendship between self and passed user"""
        return self.friends.filter(pk=user.pk).exists()

    def remove_friend(self, user):
        """Remove a friend"""
        if self.friends.filter(pk=user.pk).exists():
            self.friends.remove(user)

    def unfriend(self, user):
        """
        Initiate the action of unfriending someone.
        """
        self.remove_friend(user)
        user.friendship.remove_friend(self.user)


class FriendRequest(models.Model):
    """
    A friend request consists of two main parts:
        1. SENDER
            - Person sending/initiating the friend request
        2. RECIVER
            - Person receiving the friend friend
    """
    sender = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name='sended_friend_reqs')
    receiver = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name='received_friend_reqs')
    is_active = models.BooleanField(default=True)
    creation_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.username} -> {self.receiver.username}'
    
    def accept(self):
        """
        Accept a friend request.
        Update both SENDER and RECEIVER friendship.
        """
        self.receiver.friendship.add_friend(self.sender)
        self.sender.friendship.add_friend(self.receiver)
        self.is_active = False

    def decline(self):
        """
        Decline a friend request.
        Is it "declined" by setting the `is_active` field to False
        """
        self.is_active = False

    def cancel(self):
        """
        Cancel a friend request.
        Is it "cancelled" by setting the `is_active` field to False.
        This is only different with respect to "declining" through the notification that is generated.
        """
        self.is_active = False
