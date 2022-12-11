from django.shortcuts import get_object_or_404, HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import FriendRequest




class AcceptFriendRequestView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        friend_req_obj = get_object_or_404(FriendRequest, id=kwargs.get('pk'), receiver=request.user)
        friend_req_obj.accept()
        return HttpResponse(b"Friend request accepted!")
