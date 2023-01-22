from django.db import models
from django.contrib.auth import get_user_model




User = get_user_model()

def group_directory_path(instance, filename):
    return f'group_{instance.id}/image.png'

def get_default_image_path():
    return "default_images/group_image.png"


class GroupChatRoom(models.Model):
    """Group Chat Room Model"""
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(
        max_length=255,
        null=True,
        blank=False,
        upload_to=group_directory_path,
        default=get_default_image_path
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_groups')
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

    def save(self, *args, **kwargs) -> None:
        if self.pk:
            # Delete old group image before save the new one
            image = GroupChatRoom.objects.get(pk=self.pk).image
            if self.image.name != image.name != get_default_image_path():
                image.delete(save=False)
        return super().save(*args, **kwargs)


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
