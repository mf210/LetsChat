from django.db import models
from django.contrib.auth import get_user_model




User = get_user_model()


class PrivateChatRoom(models.Model):
    """Private Chat Room Model"""
    # name should be combination of the user's username (in alphabetical order)
    name = models.CharField(max_length=300, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class PrivateChatRoomMessage(models.Model):
    """
    Chat messages created by a user inside a PrivateChatRoom
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(PrivateChatRoom, on_delete=models.CASCADE, related_name='messages')
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    def __str__(self):
        return f'{self.room}:{self.user} | {self.timestamp} => {self.content[:20]}'

    class Meta:
        ordering = ['-timestamp']


class UnreadPrivateChatMessages(models.Model):
    """
    Keep track of the number of unread messages by a specific user in a specific private chat.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='unread_private_messages'
    )
    room = models.ForeignKey(
        PrivateChatRoom, on_delete=models.CASCADE, related_name='unread_private_messages'
    )
    most_recent_message = models.ForeignKey(PrivateChatRoomMessage, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.count} unread messages"