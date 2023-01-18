from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.views.generic import View, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from friendships.models import FriendRequest



User = get_user_model()


class ProfileView(LoginRequiredMixin, View):
    """Details of each accounts"""
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=kwargs.get('username'))
        try:
            received_friend_req = FriendRequest.objects.get(sender=user, receiver=request.user)
        except FriendRequest.DoesNotExist:
            received_friend_req = False
        try:
            sent_friend_req = FriendRequest.objects.get(sender=request.user, receiver=user)
        except FriendRequest.DoesNotExist:
            sent_friend_req = False
        context={
            'user_object': user,
            'received_friend_req': received_friend_req,
            'sent_friend_req': sent_friend_req,
            'is_friend': request.user.friendship.is_friend_with(user)
        }
        return render(request, 'accounts/profile.html', context)


class SearchAccountView(LoginRequiredMixin, View):
    """Search for accounts based on the query"""
    def get(self, request, *args, **kwargs):
        accounts = User.objects.\
            filter(username__icontains=request.GET.get('q', ' ')).\
            exclude(pk=self.request.user.pk)
        # pagination
        page_num = request.GET.get('page')
        paginator = Paginator(accounts, per_page=10)
        page_obj = paginator.get_page(page_num)
        context = {
            'page_obj': page_obj,
            'page_range': paginator.get_elided_page_range(page_obj.number),
        }
        return render(request, 'accounts/search_results.html', context)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update user's profile"""
    fields = ['username', 'profile_image', 'hide_email']
    template_name = 'accounts/edit_profile.html'

    def get_object(self, queryset=None):
        return self.request.user