from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin




class IndexView(View):
    """Index View"""
    def get(self, request, *args, **kwargs):
        return render(request, 'home/index.html')


class DashboardView(LoginRequiredMixin, View):
    """Each user has own dasboard"""
    def get(self, request, *args, **kwargs):
        return render(request, 'home/dashboard.html')


class ChatsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'home/chats.html')

