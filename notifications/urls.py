from django.urls import path

from . import views



app_name = 'notifications'

urlpatterns = [
    path('general/', views.GeneralNotificationView.as_view(), name='general'),
]