from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin




class ProfileView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(get_user_model(), username=kwargs.get('username'))
        return render(request, 'accounts/profile.html', context={'user_object': user})
