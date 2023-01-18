from django.urls import path

from . import views



app_name = 'home'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]