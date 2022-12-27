from django.db import models
from django.contrib.auth import get_user_model




User = get_user_model()



class GroupChatRoom(models.Model):
    """Group Chat Room Model"""
    name = models.CharField(max_length=255, unique=True)
    # users who are connected to chat room
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name

    @property
    def channel_name(self):
        """
        Returns the Channels Group name that sockets should subscribe to to get sent
        messages as they are generated.
        """
        return f'GroupChatRoom-{self.id}'


class GroupChatRoomMessage(models.Model):
    """
    Chat messages created by a user inside a GroupChatRoom
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(GroupChatRoom, on_delete=models.CASCADE, related_name='messages')
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    def __str__(self):
        return f'{self.room}:{self.user} | {self.timestamp} => {self.content[:20]}'

    class Meta:
        ordering = ['-timestamp']
