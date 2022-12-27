from http import HTTPStatus
import json

from django.shortcuts import render, get_object_or_404, HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import GroupChatRoom, GroupChatRoomMessage



class GroupChatRoomView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        room_name = kwargs.get('room_name')
        chat_room_obj = get_object_or_404(GroupChatRoom, name=room_name)
        if not chat_room_obj.users.filter(pk=request.user.pk).exists():
            # user is not in chat room users list (not joined)
            return render(request, 'groupchats/not_joined.html', status=HTTPStatus.FORBIDDEN)

        context = {'chat_room_obj': chat_room_obj}
        return render(request, 'groupchats/chat_room.html', context)


class GroupChatRoomMessageView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        room_name = kwargs.get('room_name')
        chat_room_obj = get_object_or_404(GroupChatRoom, name=room_name)
        if not chat_room_obj.users.filter(pk=request.user.pk).exists():
            # user is not in chat room users list (not joined)
            return HttpResponse(status=HTTPStatus.FORBIDDEN)
        # Pagination
        earliest_msg_id = request.GET.get('earliest_msg_id')
        try:
            earliest_msg = chat_room_obj.messages.get(id=earliest_msg_id)
            msg_list = chat_room_obj.messages.filter(timestamp__lt=earliest_msg.timestamp)[:10]
        except (GroupChatRoomMessage.DoesNotExist, ValueError):
            msg_list = chat_room_obj.messages.all()[:10]
        # prepare data for sending
        data = []
        for msg_obj in msg_list:
            data.append({
                'message': msg_obj.content,
                'username': msg_obj.user.username,
                'profile_image_url': msg_obj.user.profile_image.url,
                'profile_url': msg_obj.user.get_absolute_url(),
                'msg_timestamp': msg_obj.timestamp.ctime(),
                'msg_id': msg_obj.id,
            })
        return HttpResponse(json.dumps(data), content_type="application/json")
