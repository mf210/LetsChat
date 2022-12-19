from http import HTTPStatus

from django.shortcuts import render, get_object_or_404, HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

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
            friend_req_obj.cancel()
            message = 'Friend request Cancelled!'

        return HttpResponse(message)


class SendFriendRequestView(LoginRequiredMixin, View):
    """Send friend request"""
    def post(self, request, *args, **kwargs):
        receiver_id = request.POST.get('receiver_id')
        receiver = get_object_or_404(
            USER_MODEL.objects.exclude(pk=request.user.pk),
            id=receiver_id
        )
        if FriendRequest.objects.filter(sender=request.user, receiver=receiver).exists():
            status = HTTPStatus.CONFLICT
            message = f'Come on! you have sent a request to {receiver.username} before'
        else:
            FriendRequest.objects.create(sender=request.user, receiver=receiver)
            status = HTTPStatus.OK
            message = 'Request sent successfully!'

        return HttpResponse(message, status=status)


class CancelFriendRequestView(LoginRequiredMixin, View):
    """Cancel the friend request"""
    def post(self, request, *args, **kwargs):
        friend_req_pk = request.POST.get('pk')
        friend_req_obj = get_object_or_404(
            request.user.sent_friend_reqs,
            pk=friend_req_pk
        )
        friend_req_obj.cancel()
        return HttpResponse('Request cancelled successfully!')


class UnfriendView(LoginRequiredMixin, View):
    """Remove some user from a list of friends"""
    def post(self, request, *args, **kwargs):
        user = get_object_or_404(
            request.user.friendship.friends,
            pk=request.POST.get('pk')
        )
        request.user.friendship.unfriend(user)
        return HttpResponse(f'{user} removed from your friends list')


class FriendListView(LoginRequiredMixin, View):
    """List user's friends"""
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(get_user_model(), username=kwargs.get('username'))
        friends = user.friendship.friends.all()
        # pagination
        page_num = request.GET.get('page')
        paginator = Paginator(friends, per_page=10)
        page_obj = paginator.get_page(page_num)
        context = {
            'page_obj': page_obj,
            'page_range': paginator.get_elided_page_range(page_obj.number),
        }
        return render(request, 'friendships/friend_list.html', context)
