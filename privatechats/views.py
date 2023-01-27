from http import HTTPStatus
import json

from django.shortcuts import render, HttpResponse
from django.views.generic import View
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import PrivateChatRoom, PrivateChatRoomMessage
from notifications.consumers import online_users



User = get_user_model()


class PrivateChatRoomView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        friends = request.user.friendship.friends.all()
        for friend in friends:
            friend.status = 'online' if len(online_users[friend.username]) > 0 else 'offline'
        context = {
            'friends': friends,
        }
        return render(request, 'privatechats/chat_room.html', context)


class PrivateChatRoomMessageView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        roommate_username = kwargs.get('roommate')
        try:
            roommate = User.objects.get(username=roommate_username)
            if request.user.friendship.is_friend_with(roommate):
                room_name = ''.join(sorted([request.user.username, roommate_username]))
                chat_room_obj, _ = PrivateChatRoom.objects.get_or_create(name=room_name)
            else:
                return HttpResponse(status=HTTPStatus.FORBIDDEN)
        except User.DoesNotExist:
            return HttpResponse(status=HTTPStatus.NOT_FOUND)

        chat_room_messages = chat_room_obj.messages.select_related('user')
        # get earliest chat messages based on earliest_msg_id
        earliest_msg_id = request.GET.get('earliest_msg_id')
        try:
            earliest_msg = chat_room_messages.get(id=earliest_msg_id)
            msg_list = chat_room_messages.filter(timestamp__lt=earliest_msg.timestamp)
        except (PrivateChatRoomMessage.DoesNotExist, ValueError):
            msg_list = chat_room_messages
        # prepare data for sending
        data = []
        for msg_obj in msg_list[:25]:
            data.append({
                'message': msg_obj.content,
                'username': msg_obj.user.username,
                'profile_image_url': msg_obj.user.profile_image.url,
                'profile_url': msg_obj.user.get_absolute_url(),
                'msg_timestamp': msg_obj.timestamp.ctime(),
                'msg_id': msg_obj.id,
            })
        return HttpResponse(json.dumps(data), content_type="application/json")


class UnreadPrivateChatMessagesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        unread_private_messages = request.user.unread_private_messages.\
                                    select_related('sender').filter(count__gt=0)
        data = []
        for upm in unread_private_messages:
            data.append({
                'id': upm.id,
                'count': upm.count,
                'most_recent_message': upm.most_recent_message,
                'most_recent_message_timestamp': upm.timestamp.isoformat(),
                'sender_username': upm.sender.username,
                'sender_profile_image': upm.sender.profile_image.url,
            })
        return HttpResponse(json.dumps(data), content_type="application/json")

