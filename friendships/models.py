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

