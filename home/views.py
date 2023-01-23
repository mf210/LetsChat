import json

from django.shortcuts import HttpResponse, render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from groupchats.models import GroupChatRoom, GroupChatRoomMessage




class IndexView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('groupchats:chat-room', room_name='public')
        return render(request, 'home/index.html')


class DashboardView(LoginRequiredMixin, View):
    """Each user has own dasboard"""
    def get(self, request, *args, **kwargs):
        return render(request, 'home/dashboard.html')


class ChatsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        friends = request.user.friendship.friends.all()
        context = {
            'friends': friends,
        }
        return render(request, 'home/chats.html', context)


class PublicChatRoomMessagesView(View):
    def get(self, request, *args, **kwargs):
        public_chat_room_msgs = GroupChatRoom.objects.get(name='public').\
                                messages.select_related('user')
        # get earliest chat messages based on earliest_msg_id
        earliest_msg_id = request.GET.get('earliest_msg_id')
        try:
            earliest_msg = public_chat_room_msgs.get(id=earliest_msg_id)
            msg_list = public_chat_room_msgs.filter(timestamp__lt=earliest_msg.timestamp)
        except (GroupChatRoomMessage.DoesNotExist, ValueError):
            msg_list = public_chat_room_msgs
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