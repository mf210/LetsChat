from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Friendship



USER_MODEL = get_user_model()


@receiver(post_save, sender=USER_MODEL)
def create_friendship(sender, instance, created, **kwargs):
    if created:
        Friendship.objects.create(user=instance)