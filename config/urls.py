from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('', include('home.urls')),
    path('admin/', admin.site.urls),
    path('account/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),
    path('friendships/', include('friendships.urls')),
    path('groupchats/', include('groupchats.urls')),
    path('privatechats/', include('privatechats.urls')),
    path('notifications/', include('notifications.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)