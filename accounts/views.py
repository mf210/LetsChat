from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator




class ProfileView(LoginRequiredMixin, View):
    """Details of each accounts"""
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(get_user_model(), username=kwargs.get('username'))
        return render(request, 'accounts/profile.html', context={'user_object': user})


class SearchAccountView(LoginRequiredMixin, View):
    """Search for accounts based on the query"""
    def get(self, request, *args, **kwargs):
        accounts = get_user_model().\
                objects.filter(username__icontains=request.GET.get('q', ' ')).\
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
