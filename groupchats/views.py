from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import GroupChatRoom



class GroupChatRoomView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        room_name = kwargs.get('room_name')
        context = {
            'chat_room_obj': get_object_or_404(GroupChatRoom, name=room_name),
        }
        return render(request, 'groupchats/chat_room.html', context)
