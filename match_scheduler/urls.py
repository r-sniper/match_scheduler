from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^', include('home.urls')),
    url(r'^admin/', admin.site.urls),
    url('', include('social_django.urls', namespace='social')),
    url('', include('django.contrib.auth.urls', namespace='auth')),



]
