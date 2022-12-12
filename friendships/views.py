from django.shortcuts import get_object_or_404, HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import FriendRequest




class HandleFriendRequestView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        friend_req_obj = get_object_or_404(FriendRequest, id=kwargs.get('pk'), receiver=request.user)
        accept = True if request.POST.get('accept') == 'true' else False
        if accept:
            friend_req_obj.accept()
            message = 'Friend request accepted!'
        else:
            friend_req_obj.decline()
            message = 'Friend request declined!'

        return HttpResponse(message)
