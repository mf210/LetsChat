from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model




User = get_user_model()


class Notification(models.Model):
    """Notification Model with A generic type that can refer to a FriendRequest, Unread Message, or any other type of notification"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    verb = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return self.verb

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]