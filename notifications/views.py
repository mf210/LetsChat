import json

from django.shortcuts import HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Notification




class GeneralNotificationView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        all_general_notifs = request.user.notifications.all()
        # get earliest notification based on earliest_notif_id
        earliest_notif_id = request.GET.get('earliest_notif_id')
        try:
            earliest_notif = all_general_notifs.get(id=earliest_notif_id)
            notifs_list = all_general_notifs.filter(timestamp__lt=earliest_notif.timestamp)
        except (Notification.DoesNotExist, ValueError):
            notifs_list = request.user.notifications.all()
        # prepare data for sending
        data = []
        for notif_obj in notifs_list[:5]:
            content_type = notif_obj.content_type.app_labeled_name
            if content_type == 'friendships | friendship':
                sender = notif_obj.content_object.user
            elif content_type == 'friendships | friend request':
                sender = notif_obj.content_object.sender
            data.append({
                'verb': notif_obj.verb,
                'timestamp': notif_obj.timestamp.isoformat(),
                'is_read': notif_obj.is_read,
                'profile_url': sender.get_absolute_url(),
                'image_url': sender.profile_image.url,
                'content_type': content_type,
                'content_object_id': notif_obj.content_object.id,
                'notification_id': notif_obj.id,
            })
        return HttpResponse(json.dumps(data), content_type="application/json")
    