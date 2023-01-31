import sys

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import GroupChatRoom



User = get_user_model()



if not (('/usr/local/bin/pytest' in sys.argv) or ('test' in sys.argv)):
    @receiver(post_save, sender=User)
    def add_user_to_public_group_chat_room(sender, instance, created, **kwargs):
        if created:
            GroupChatRoom.objects.get(name='public').users.add(instance)