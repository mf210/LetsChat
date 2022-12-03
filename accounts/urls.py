from django.urls import path

from . import views



app_name = 'accounts'

urlpatterns = [
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),
    path('search/', views.SearchAccountView.as_view(), name='search'),
]