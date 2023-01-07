from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model




User = get_user_model()


class Notification(models.Model):
    # Who the notification is sent to
    target = models.ForeignKey(User, on_delete=models.CASCADE)
    # The user that the creation of the notification was triggered by.
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="from_user")
    redirect_url = models.URLField(max_length=500, blank=True, help_text="The URL to be visited when a notification is clicked.")
    # statement describing the notification (ex: "Mitch sent you a friend request")
    verb = models.CharField(max_length=255, blank=True)
    # When the notification was created/updated
    timestamp = models.DateTimeField(auto_now_add=True)
    # Some notifications can be marked as "read". (I used "read" instead of "active". I think its more appropriate)
    read = models.BooleanField(default=False)
    # A generic type that can refer to a FriendRequest, Unread Message, or any other type of "Notification"
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return self.verb

    def get_content_object_type(self):
        return str(self.content_object.get_cname)
