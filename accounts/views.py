from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView





class ProfileView(TemplateView):
    template_name: str = 'accounts/profile.html'
