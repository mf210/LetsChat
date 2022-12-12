from http import HTTPStatus

from django.shortcuts import get_object_or_404, HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from .models import FriendRequest


USER_MODEL = get_user_model()


class HandleFriendRequestView(LoginRequiredMixin, View):
    """Accept, Decline or cancel friend request"""
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


class SendFriendRequestView(LoginRequiredMixin, View):
    """Send friend request"""
    def post(self, request, *args, **kwargs):
        receiver_username = request.POST.get('receiver_username')
        receiver = get_object_or_404(
            USER_MODEL.objects.exclude(pk=request.user.pk),
            username=receiver_username
        )
        if FriendRequest.objects.filter(sender=request.user, receiver=receiver).exists():
            status = HTTPStatus.CONFLICT
            message = f'Come on! you have sent a request to {receiver.username} before'
        else:
            FriendRequest.objects.create(sender=request.user, receiver=receiver)
            status = HTTPStatus.OK
            message = 'Request sent successfully!'

        return HttpResponse(message, status=status)


