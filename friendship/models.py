from django.db import models
from django.contrib.auth import get_user_model


USER_MODEL = get_user_model()



class Friendship(models.Model):
    user = models.OneToOneField(USER_MODEL, on_delete=models.CASCADE, related_name='user')
    friends = models.ManyToManyField(USER_MODEL, blank=True, related_name='friends')

    def __str__(self):
        return self.user.username
