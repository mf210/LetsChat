from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin





class PrivateChatRoomView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        friends = request.user.friendship.friends.all()
        context = {
            'friends': friends,
        }
        return render(request, 'privatechats/chat_room.html', context)
