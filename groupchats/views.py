from http import HTTPStatus

from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import GroupChatRoom



class GroupChatRoomView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        room_name = kwargs.get('room_name')
        chat_room_obj = get_object_or_404(GroupChatRoom, name=room_name)
        if not chat_room_obj.users.filter(pk=request.user.pk).exists():
            # user did not join to the chat room
            return render(request, 'groupchats/not_joined.html', status=HTTPStatus.FORBIDDEN)

        context = {'chat_room_obj': chat_room_obj}
        return render(request, 'groupchats/chat_room.html', context)
